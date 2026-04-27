from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
import hashlib
import hmac

import httpx

from app.config import settings


@dataclass(frozen=True)
class PayazaVirtualAccount:
    account_number: str
    account_name: str
    bank_name: str
    bank_code: str
    reference: str


@dataclass(frozen=True)
class PayazaPaymentLink:
    payment_url: str
    reference: str


class PayazaError(RuntimeError):
    pass


def _extract_payload(response_json: dict) -> dict:
    if isinstance(response_json.get("data"), dict):
        return response_json["data"]
    return response_json


def _extract_payment_url(payload: dict) -> str:
    for key in ("payment_url", "authorization_url", "link", "url"):
        value = payload.get(key)
        if value:
            return str(value)
    raise PayazaError("Payaza response missing payment URL")


def verify_hmac_sha512(raw_body: bytes, signature: str, secret: str | None = None) -> bool:
    if not signature:
        return False
    secret_value = secret or settings.payaza_secret_key
    if not secret_value:
        return False
    expected = hmac.new(secret_value.encode("utf-8"), raw_body, hashlib.sha512).hexdigest()
    return hmac.compare_digest(expected, signature)


async def create_virtual_account(
    first_name: str,
    last_name: str,
    phone: str,
    email: str,
    reference: str,
) -> PayazaVirtualAccount:
    if not settings.payaza_secret_key:
        raise PayazaError("Payaza secret key is not configured.")

    url = f"{settings.payaza_base_url}{settings.payaza_dva_endpoint}"
    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "phone": phone,
        "email": email,
        "reference": reference,
    }
    headers = {
        "Authorization": f"Payaza {settings.payaza_secret_key}",
        "Content-Type": "application/json",
    }

    timeout = httpx.Timeout(settings.payaza_timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(url, json=payload, headers=headers)

    if response.status_code >= 400:
        raise PayazaError(f"Payaza DVA request failed ({response.status_code}).")

    data = _extract_payload(response.json())
    required = ["account_number", "account_name", "bank_name", "bank_code", "reference"]
    missing = [key for key in required if not data.get(key)]
    if missing:
        raise PayazaError("Payaza response missing fields: " + ", ".join(missing))

    return PayazaVirtualAccount(
        account_number=str(data["account_number"]),
        account_name=str(data["account_name"]),
        bank_name=str(data["bank_name"]),
        bank_code=str(data["bank_code"]),
        reference=str(data["reference"]),
    )


async def create_payment_link(
    amount: Decimal,
    email: str,
    reference: str,
    metadata: dict | None = None,
    callback_url: str | None = None,
    currency: str = "NGN",
) -> PayazaPaymentLink:
    if not settings.payaza_secret_key:
        raise PayazaError("Payaza secret key is not configured.")
    if not settings.payaza_payment_link_endpoint:
        raise PayazaError("Payaza payment link endpoint is not configured.")
    if amount <= 0:
        raise PayazaError("Amount must be positive.")

    url = f"{settings.payaza_base_url}{settings.payaza_payment_link_endpoint}"
    payload = {
        "amount": str(amount),
        "email": email,
        "reference": reference,
        "currency": currency,
    }
    if metadata:
        payload["metadata"] = metadata
    if callback_url:
        payload["callback_url"] = callback_url

    headers = {
        "Authorization": f"Payaza {settings.payaza_secret_key}",
        "Content-Type": "application/json",
    }

    timeout = httpx.Timeout(settings.payaza_timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(url, json=payload, headers=headers)

    if response.status_code >= 400:
        raise PayazaError(f"Payaza payment link request failed ({response.status_code}).")

    data = _extract_payload(response.json())
    payment_url = _extract_payment_url(data)
    ref_value = str(data.get("reference") or reference)
    return PayazaPaymentLink(payment_url=payment_url, reference=ref_value)
