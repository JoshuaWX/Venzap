from __future__ import annotations

import json
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models import Transaction, User, Wallet
from app.utils.helpers import normalize_email


def _to_decimal(value) -> Decimal:
    try:
        return Decimal(str(value))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid amount") from exc


def _ensure_positive(amount: Decimal) -> None:
    if amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be positive")


def _validate_transaction_type(transaction_type: str) -> None:
    allowed = {"credit", "debit", "escrow", "release"}
    if transaction_type not in allowed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid transaction type")


def _validate_source(source: str) -> None:
    allowed = {"virtual_account", "payment_link", "order_debit", "escrow_release"}
    if source not in allowed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid transaction source")


def _parse_metadata(payload: dict) -> dict:
    metadata = payload.get("metadata")
    if isinstance(metadata, dict):
        return metadata
    if isinstance(metadata, str):
        try:
            parsed = json.loads(metadata)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            return {}
    return {}


async def _get_wallet_for_update(session: AsyncSession, user_id: str) -> Wallet:
    wallet = await session.scalar(
        select(Wallet).where(Wallet.user_id == user_id).with_for_update()
    )
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
    return wallet


async def _get_wallet(session: AsyncSession, user_id: str) -> Wallet:
    wallet = await session.scalar(select(Wallet).where(Wallet.user_id == user_id))
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
    return wallet


async def get_balance(session: AsyncSession, user_id: str) -> Decimal:
    wallet = await _get_wallet(session, user_id)
    return wallet.balance


async def credit_wallet(
    session: AsyncSession,
    user_id: str,
    amount: Decimal,
    reference: str,
    source: str,
    payaza_ref: str | None = None,
    description: str | None = None,
    transaction_type: str = "credit",
) -> Transaction:
    _validate_transaction_type(transaction_type)
    _validate_source(source)
    _ensure_positive(amount)

    existing = await session.scalar(select(Transaction).where(Transaction.reference == reference))
    if existing:
        return existing

    try:
        async with session.begin():
            wallet = await _get_wallet_for_update(session, user_id)
            wallet.balance = (wallet.balance or Decimal("0.00")) + amount
            transaction = Transaction(
                wallet_id=wallet.id,
                type=transaction_type,
                amount=amount,
                reference=reference,
                payaza_ref=payaza_ref,
                source=source,
                status="success",
                description=description,
            )
            session.add(transaction)
        return transaction
    except IntegrityError:
        await session.rollback()
        existing = await session.scalar(select(Transaction).where(Transaction.reference == reference))
        if existing:
            return existing
        raise


async def debit_wallet(
    session: AsyncSession,
    user_id: str,
    amount: Decimal,
    reference: str,
    source: str,
    payaza_ref: str | None = None,
    description: str | None = None,
    transaction_type: str = "debit",
) -> Transaction:
    _validate_transaction_type(transaction_type)
    _validate_source(source)
    _ensure_positive(amount)

    existing = await session.scalar(select(Transaction).where(Transaction.reference == reference))
    if existing:
        return existing

    try:
        async with session.begin():
            wallet = await _get_wallet_for_update(session, user_id)
            if wallet.balance is None or wallet.balance < amount:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")
            wallet.balance = wallet.balance - amount
            transaction = Transaction(
                wallet_id=wallet.id,
                type=transaction_type,
                amount=amount,
                reference=reference,
                payaza_ref=payaza_ref,
                source=source,
                status="success",
                description=description,
            )
            session.add(transaction)
        return transaction
    except IntegrityError:
        await session.rollback()
        existing = await session.scalar(select(Transaction).where(Transaction.reference == reference))
        if existing:
            return existing
        raise


async def handle_payment_link_credit(payload: dict) -> None:
    amount = _to_decimal(payload.get("amount"))
    _ensure_positive(amount)

    reference = str(payload.get("reference") or payload.get("id") or "").strip()
    if not reference:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing payment reference")

    metadata = _parse_metadata(payload)
    user_id = metadata.get("user_id") or payload.get("user_id")
    user_email = payload.get("email") or payload.get("customer_email") or payload.get("customer", {}).get("email")

    async with AsyncSessionLocal() as session:
        if user_id:
            try:
                user_id = str(UUID(str(user_id)))
            except ValueError as exc:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id") from exc
            user = await session.get(User, user_id)
        elif user_email:
            user = await session.scalar(select(User).where(User.email == normalize_email(str(user_email))))
        else:
            user = None

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found for payment link")

        await credit_wallet(
            session=session,
            user_id=str(user.id),
            amount=amount,
            reference=reference,
            source="payment_link",
            payaza_ref=str(payload.get("payaza_ref") or reference),
            description="Wallet credit via payment link",
        )
