from __future__ import annotations

import ssl
import smtplib
from email.message import EmailMessage
import logging

import anyio

from app.config import settings

logger = logging.getLogger(__name__)


def _send_email_sync(to_email: str, subject: str, html_body: str, text_body: str) -> None:
    if not settings.smtp_host or not settings.smtp_user or not settings.smtp_password:
        logger.warning(f"SMTP not configured, skipping email to {to_email}: {subject}")
        return

    message = EmailMessage()
    message["From"] = settings.smtp_user
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(text_body)
    message.add_alternative(html_body, subtype="html")

    context = ssl.create_default_context()
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls(context=context)
        server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(message)


async def send_email(to_email: str, subject: str, html_body: str, text_body: str) -> None:
    await anyio.to_thread.run_sync(_send_email_sync, to_email, subject, html_body, text_body)


async def send_otp_email(to_email: str, otp_code: str, purpose: str) -> None:
    subject = "Venzap verification code"
    if purpose == "password_reset":
        subject = "Venzap password reset code"

    text_body = (
        "Your Venzap verification code is: {code}\n"
        "This code expires in {minutes} minutes."
    ).format(code=otp_code, minutes=int(settings.otp_ttl_seconds / 60))

    html_body = (
        "<p>Your Venzap verification code is:</p>"
        "<h2>{code}</h2>"
        "<p>This code expires in {minutes} minutes.</p>"
    ).format(code=otp_code, minutes=int(settings.otp_ttl_seconds / 60))

    await send_email(to_email, subject, html_body, text_body)
