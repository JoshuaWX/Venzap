from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hmac

from fastapi import HTTPException, status
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import User, Vendor, Wallet
from app.redis_client import get_redis_client
from app.services.email_service import send_otp_email
from app.utils.constants import OTP_PREFIX, REFRESH_TOKEN_PREFIX
from app.utils.helpers import generate_otp, hash_otp, normalize_email
from app.utils.security import (
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str


async def _store_refresh_token(jti: str, subject: str, expires_at: datetime) -> None:
    redis = get_redis_client()
    ttl = max(1, int((expires_at - datetime.now(timezone.utc)).total_seconds()))
    await redis.setex(f"{REFRESH_TOKEN_PREFIX}{jti}", ttl, subject)


async def _revoke_refresh_token(jti: str) -> None:
    redis = get_redis_client()
    await redis.delete(f"{REFRESH_TOKEN_PREFIX}{jti}")


async def issue_token_pair(subject: str, role: str) -> TokenPair:
    access_token = create_access_token(subject=subject, role=role)
    refresh_token, jti, expires_at = create_refresh_token(subject=subject, role=role)
    await _store_refresh_token(jti, subject, expires_at)
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


async def rotate_refresh_token(refresh_token: str) -> TokenPair:
    try:
        payload = decode_token(refresh_token)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    if payload.get("type") != REFRESH_TOKEN_TYPE:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token type")

    jti = payload.get("jti")
    subject = payload.get("sub")
    role = payload.get("role")
    if not jti or not subject or not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    redis = get_redis_client()
    key = f"{REFRESH_TOKEN_PREFIX}{jti}"
    if not await redis.get(key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")

    await _revoke_refresh_token(jti)
    return await issue_token_pair(subject=subject, role=role)


async def send_otp(email: str, purpose: str) -> None:
    if not settings.secret_key:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server misconfigured")

    email = normalize_email(email)
    otp_code = generate_otp()
    hashed = hash_otp(otp_code, settings.secret_key)

    redis = get_redis_client()
    key = f"{OTP_PREFIX}:{purpose}:{email}"
    await redis.setex(key, settings.otp_ttl_seconds, hashed)
    # In development, log the OTP so tests can read it from logs when email sending
    logger = logging.getLogger(__name__)
    if settings.environment and settings.environment.lower() == "development":
        logger.warning(f"DEV OTP for {email} (purpose={purpose}): {otp_code}")

    await send_otp_email(email, otp_code, purpose)


async def verify_otp(email: str, purpose: str, otp: str) -> bool:
    email = normalize_email(email)
    redis = get_redis_client()
    key = f"{OTP_PREFIX}:{purpose}:{email}"
    stored = await redis.get(key)
    if not stored:
        return False

    hashed = hash_otp(otp, settings.secret_key)
    if not hmac_compare(stored, hashed):
        return False

    await redis.delete(key)
    return True


def hmac_compare(a: str, b: str) -> bool:
    return hmac.compare_digest(a, b)


async def register_vendor(session: AsyncSession, payload) -> Vendor:
    email = normalize_email(payload.email)

    existing = await session.scalar(select(Vendor).where(Vendor.email == email))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    existing_phone = await session.scalar(select(Vendor).where(Vendor.phone == payload.phone))
    if existing_phone:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone already registered")

    existing_name = await session.scalar(select(Vendor).where(Vendor.business_name == payload.business_name))
    if existing_name:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Business name already registered")

    vendor = Vendor(
        business_name=payload.business_name,
        email=email,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        address=payload.address,
        description=payload.description,
        logo_url=payload.logo_url,
        vendor_type=payload.vendor_type,
        delivery_fee=payload.delivery_fee,
        is_verified=False,
    )

    session.add(vendor)
    await session.commit()
    await session.refresh(vendor)
    
    # Create User record for vendor so DVA provisioning can work
    # (VirtualAccount references User, not Vendor)
    try:
        user = await get_or_create_user_from_vendor(session, vendor)
        # Import here to avoid circular dependency during module load
        from app.services.virtual_account_service import queue_virtual_account_provisioning
        queue_virtual_account_provisioning(str(user.id))
    except Exception:
        logger = logging.getLogger(__name__)
        logger.exception("Failed to queue DVA provisioning for vendor %s", vendor.id)
    
    return vendor


async def register_user(session: AsyncSession, payload) -> User:
    email = normalize_email(payload.email)

    existing = await session.scalar(select(User).where(User.email == email))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    existing_phone = await session.scalar(select(User).where(User.phone == payload.phone))
    if existing_phone:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone already registered")

    user = User(
        full_name=payload.full_name,
        email=email,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        is_verified=False,
    )

    wallet = Wallet(user=user)

    session.add_all([user, wallet])
    await session.commit()
    await session.refresh(user)
    
    # Queue Payaza DVA provisioning for user (non-blocking)
    try:
        # Import here to avoid circular dependency during module load
        from app.services.virtual_account_service import queue_virtual_account_provisioning
        queue_virtual_account_provisioning(str(user.id))
    except Exception:
        logger = logging.getLogger(__name__)
        logger.exception("Failed to queue DVA provisioning for user %s", user.id)
    
    return user


async def get_vendor_by_email(session: AsyncSession, email: str) -> Vendor | None:
    return await session.scalar(select(Vendor).where(Vendor.email == normalize_email(email)))


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    return await session.scalar(select(User).where(User.email == normalize_email(email)))


async def authenticate_vendor(session: AsyncSession, email: str, password: str) -> Vendor:
    vendor = await get_vendor_by_email(session, email)
    if not vendor or not verify_password(password, vendor.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not vendor.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vendor account disabled")
    # Email verification not required for login (DVA provisioning happens asynchronously)
    return vendor


async def authenticate_user(session: AsyncSession, email: str, password: str) -> User:
    user = await get_user_by_email(session, email)
    if not user or not user.password_hash or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account disabled")
    # Email verification not required for login (DVA provisioning happens asynchronously)
    return user


async def mark_vendor_verified(session: AsyncSession, vendor: Vendor) -> None:
    vendor.is_verified = True
    await session.commit()


async def mark_user_verified(session: AsyncSession, user: User) -> None:
    user.is_verified = True
    await session.commit()


async def update_vendor_password(session: AsyncSession, vendor: Vendor, new_password: str) -> None:
    vendor.password_hash = hash_password(new_password)
    await session.commit()


async def update_user_password(session: AsyncSession, user: User, new_password: str) -> None:
    user.password_hash = hash_password(new_password)
    await session.commit()


async def get_or_create_user_from_vendor(session: AsyncSession, vendor: Vendor) -> User:
    """
    Create a User record for a vendor to enable DVA provisioning.
    Vendors need User records because VirtualAccount references User, not Vendor.
    If User already exists for this vendor (by email), return it.
    Otherwise, create a new User using vendor details.
    """
    existing_user = await get_user_by_email(session, vendor.email)
    if existing_user:
        return existing_user

    user = User(
        full_name=vendor.business_name,
        email=vendor.email,
        phone=vendor.phone,
        password_hash=vendor.password_hash,
        is_verified=False,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
