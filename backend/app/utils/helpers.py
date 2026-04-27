from __future__ import annotations

import hashlib
import hmac
import re
import secrets
from typing import Iterable

from app.utils.constants import OTP_LENGTH


_TAG_RE = re.compile(r"<[^>]+>")
_PHONE_RE = re.compile(r"^(070|080|081|090|091)\d{8}$")


def sanitize_text(value: str) -> str:
    cleaned = _TAG_RE.sub("", value)
    cleaned = " ".join(cleaned.split()).strip()
    return cleaned


def normalize_email(email: str) -> str:
    return email.strip().lower()


def is_valid_phone(phone: str) -> bool:
    return bool(_PHONE_RE.match(phone))


def generate_otp(length: int = OTP_LENGTH) -> str:
    upper = 10**length
    otp = secrets.randbelow(upper)
    return str(otp).zfill(length)


def hash_otp(otp: str, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), otp.encode("utf-8"), hashlib.sha256).hexdigest()


def ensure_non_empty(values: Iterable[str]) -> bool:
    return all(value.strip() for value in values)


def split_full_name(full_name: str) -> tuple[str, str]:
    parts = [part for part in full_name.split() if part]
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])
