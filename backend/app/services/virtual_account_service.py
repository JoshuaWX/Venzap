from __future__ import annotations

import asyncio
from dataclasses import dataclass
import logging
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.celery_app import celery_app
from app.config import settings
from app.database import AsyncSessionLocal
from app.models import Transaction, User, VirtualAccount, Wallet
from app.redis_client import get_redis_client
from app.services.email_service import send_email
from app.services.payaza_service import PayazaError, create_virtual_account
from app.utils.constants import DVA_CACHE_TTL_SECONDS
from app.utils.helpers import normalize_email, split_full_name


@dataclass(frozen=True)
class ProvisioningResult:
    account_number: str
    account_name: str
    bank_name: str


class ProvisioningError(RuntimeError):
    pass


logger = logging.getLogger("venzap.dva")


def _cache_key(account_number: str) -> str:
    return f"dva:user:{account_number}"


def _to_decimal(value) -> Decimal:
    return Decimal(str(value))


async def _cache_account(account_number: str, user_id: str) -> None:
    redis = get_redis_client()
    await redis.setex(_cache_key(account_number), DVA_CACHE_TTL_SECONDS, user_id)


async def _get_cached_user_id(account_number: str) -> str | None:
    redis = get_redis_client()
    key = _cache_key(account_number)
    user_id = await redis.get(key)
    if user_id:
        await redis.expire(key, DVA_CACHE_TTL_SECONDS)
    return user_id


async def _get_user_by_account_number(session: AsyncSession, account_number: str) -> User | None:
    cached_user_id = await _get_cached_user_id(account_number)
    if cached_user_id:
        return await session.get(User, cached_user_id)

    stmt = (
        select(User)
        .join(VirtualAccount, VirtualAccount.user_id == User.id)
        .where(VirtualAccount.account_number == account_number)
    )
    user = await session.scalar(stmt)
    if user:
        await _cache_account(account_number, str(user.id))
    return user


async def provision_virtual_account(user: User) -> VirtualAccount:
    logger.info("DVA provision start user_id=%s", user.id)
    async with AsyncSessionLocal() as session:
        existing = await session.scalar(select(VirtualAccount).where(VirtualAccount.user_id == user.id))
        if existing:
            logger.info("DVA exists user_id=%s account=%s", user.id, existing.account_number)
            await _cache_account(existing.account_number, str(user.id))
            return existing

        first_name, last_name = split_full_name(user.full_name)
        if not first_name:
            raise ProvisioningError("Invalid user name")

        try:
            dva = await create_virtual_account(
                first_name=first_name,
                last_name=last_name,
                phone=user.phone,
                email=normalize_email(user.email),
                reference=str(user.id),
            )
        except PayazaError as exc:
            logger.exception("DVA provision failed user_id=%s", user.id)
            raise ProvisioningError(str(exc)) from exc

        virtual_account = VirtualAccount(
            user_id=user.id,
            account_number=dva.account_number,
            account_name=dva.account_name,
            bank_name=dva.bank_name,
            bank_code=dva.bank_code,
            payaza_ref=dva.reference,
            is_active=True,
        )
        session.add(virtual_account)
        await session.commit()
        await session.refresh(virtual_account)

        logger.info("DVA provisioned user_id=%s account=%s", user.id, virtual_account.account_number)

        await _cache_account(virtual_account.account_number, str(user.id))
        return virtual_account


async def get_user_by_account_number(acct_no: str) -> User:
    async with AsyncSessionLocal() as session:
        user = await _get_user_by_account_number(session, acct_no)
        if not user:
            raise ProvisioningError("User not found for account number")
        return user


async def handle_dva_credit(payload: dict) -> None:
    account_number = str(payload.get("account_number") or "").strip()
    reference = str(payload.get("reference") or payload.get("id") or "").strip()
    sender = str(payload.get("sender") or "").strip()

    logger.info("DVA credit received account=%s reference=%s", account_number, reference)

    if not account_number or not reference:
        raise ProvisioningError("Missing account number or reference")

    amount_value = payload.get("amount")
    amount = _to_decimal(amount_value)
    if amount <= 0:
        raise ProvisioningError("Invalid amount")

    async with AsyncSessionLocal() as session:
        existing_txn = await session.scalar(select(Transaction).where(Transaction.reference == reference))
        if existing_txn:
            return

        user = await _get_user_by_account_number(session, account_number)
        if not user:
            raise ProvisioningError("User not found for account number")

        wallet = await session.scalar(
            select(Wallet).where(Wallet.user_id == user.id).with_for_update()
        )
        if not wallet:
            raise ProvisioningError("Wallet not found for user")

        description = f"Wallet credit from {sender}" if sender else "Wallet credit"
        wallet.balance = (wallet.balance or Decimal("0.00")) + amount
        transaction = Transaction(
            wallet_id=wallet.id,
            type="credit",
            amount=amount,
            reference=reference,
            payaza_ref=reference,
            source="virtual_account",
            status="success",
            description=description,
        )
        session.add(transaction)
        await session.commit()


def queue_virtual_account_provisioning(user_id: str) -> None:
    logger.info("DVA queue requested user_id=%s", user_id)
    try:
        provision_virtual_account_task.delay(user_id)
    except Exception:
        try:
            asyncio.run(_provision_by_user_id(user_id))
        except Exception:
            logger.exception("Failed to provision virtual account for user %s", user_id)


@celery_app.task(bind=True, max_retries=3)
def provision_virtual_account_task(self, user_id: str) -> None:
    try:
        asyncio.run(_provision_by_user_id(user_id))
    except Exception as exc:  # noqa: BLE001
        if self.request.retries >= 2:
            asyncio.run(_notify_provisioning_failure(user_id, str(exc)))
        raise self.retry(exc=exc, countdown=60)


async def _notify_provisioning_failure(user_id: str, error: str) -> None:
    subject = "Venzap DVA provisioning failed"
    text_body = f"Virtual account provisioning failed for user {user_id}. Error: {error}"
    html_body = f"<p>Virtual account provisioning failed for user {user_id}.</p><p>Error: {error}</p>"
    await send_email(settings.support_email, subject, html_body, text_body)


async def _provision_by_user_id(user_id: str) -> None:
    async with AsyncSessionLocal() as session:
        user = await session.get(User, user_id)
        if not user:
            raise ProvisioningError("User not found")

    await provision_virtual_account(user)
