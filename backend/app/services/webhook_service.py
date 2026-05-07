from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models import WebhookEvent
from app.services import virtual_account_service, wallet_service


logger = logging.getLogger("venzap.webhooks")


def _get_event_type(payload: dict) -> str:
    return str(payload.get("event") or payload.get("type") or "unknown")


async def _get_or_create_event(session: AsyncSession, payaza_ref: str, event_type: str, payload: dict) -> WebhookEvent:
    existing = await session.scalar(select(WebhookEvent).where(WebhookEvent.payaza_ref == payaza_ref))
    if existing:
        return existing

    event = WebhookEvent(
        event_type=event_type,
        payaza_ref=payaza_ref,
        payload=payload,
        processed=False,
    )
    session.add(event)
    try:
        await session.flush()
        return event
    except IntegrityError:
        await session.rollback()
        existing = await session.scalar(select(WebhookEvent).where(WebhookEvent.payaza_ref == payaza_ref))
        if existing:
            return existing
        raise


async def _mark_processed(session: AsyncSession, event: WebhookEvent) -> None:
    event.processed = True
    event.processed_at = datetime.now(timezone.utc)
    event.error = None
    await session.flush()


async def _mark_error(session: AsyncSession, event: WebhookEvent, error: str) -> None:
    event.error = error[:1000]
    await session.flush()


async def _process_event(payload: dict, payaza_ref: str) -> None:
    event_type = _get_event_type(payload)

    async with AsyncSessionLocal() as session:
        existing = await session.scalar(select(WebhookEvent).where(WebhookEvent.payaza_ref == payaza_ref))
        if existing and existing.processed:
            return

        event = await _get_or_create_event(session, payaza_ref, event_type, payload)
        await session.commit()

    try:
        if event_type == "virtual_account.credit":
            await virtual_account_service.handle_dva_credit(payload)
        elif event_type == "payment.success":
            await wallet_service.handle_payment_link_credit(payload)
        elif event_type == "transfer.success":
            logger.info("Transfer success webhook received: %s", payaza_ref)
        else:
            logger.info("Unhandled Payaza event: %s", event_type)

        async with AsyncSessionLocal() as session:
            event = await session.scalar(select(WebhookEvent).where(WebhookEvent.payaza_ref == payaza_ref))
            if event and not event.processed:
                await _mark_processed(session, event)
                await session.commit()

    except Exception as exc:  # noqa: BLE001
        async with AsyncSessionLocal() as session:
            event = await session.scalar(select(WebhookEvent).where(WebhookEvent.payaza_ref == payaza_ref))
            if event:
                await _mark_error(session, event, str(exc))
                await session.commit()
        raise


@celery_app.task(bind=True, max_retries=3)
def process_payaza_webhook(self, payload: dict, payaza_ref: str) -> None:
    try:
        asyncio.run(_process_event(payload, payaza_ref))
    except Exception as exc:  # noqa: BLE001
        raise self.retry(exc=exc, countdown=60)


def queue_payaza_webhook(payload: dict, payaza_ref: str) -> None:
    try:
        process_payaza_webhook.delay(payload, payaza_ref)
    except Exception:
        asyncio.run(_process_event(payload, payaza_ref))


def parse_json_body(raw_body: bytes) -> dict[str, Any] | None:
    try:
        data = json.loads(raw_body)
    except json.JSONDecodeError:
        return None
    if isinstance(data, dict):
        return data
    return None
