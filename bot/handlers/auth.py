from __future__ import annotations

import logging
import re

from telegram import Update
from telegram.ext import ContextTypes

from bot.keyboards.auth_keyboard import build_auth_keyboard, build_start_keyboard
from bot.keyboards.order_keyboard import build_main_menu
from bot.services import api_client
from bot.state import redis_state
from bot.utils import formatters


SIGNUP_FULL_NAME = "AUTH_SIGNUP_FULL_NAME"
SIGNUP_EMAIL = "AUTH_SIGNUP_EMAIL"
SIGNUP_PHONE = "AUTH_SIGNUP_PHONE"
SIGNUP_PASSWORD = "AUTH_SIGNUP_PASSWORD"
LOGIN_EMAIL = "AUTH_LOGIN_EMAIL"
LOGIN_PASSWORD = "AUTH_LOGIN_PASSWORD"

logger = logging.getLogger("venzap.bot.auth")


def _is_email(value: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value.strip()))


def _is_nigerian_phone(value: str) -> bool:
    return bool(re.match(r"^(?:0|\+234)(?:70|80|81|90|91)\d{8}$", value.strip()))


def _mask_email(value: str) -> str:
    value = value.strip()
    if "@" not in value:
        return (value[:1] + "***") if value else "***"
    name, domain = value.split("@", 1)
    if not name:
        return f"***@{domain}"
    return f"{name[0]}***@{domain}"


async def start_signup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return

    logger.info("Signup started telegram_id=%s", user.id)
    await redis_state.clear_registration(user.id)
    await redis_state.clear_auth_cookies(user.id)
    await redis_state.set_state(user.id, SIGNUP_FULL_NAME)
    await message.reply_text("What is your full name?", reply_markup=build_auth_keyboard())


async def start_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return

    logger.info("Login started telegram_id=%s", user.id)
    await redis_state.clear_registration(user.id)
    await redis_state.set_state(user.id, LOGIN_EMAIL)
    await message.reply_text("Enter your email address.", reply_markup=build_auth_keyboard())


async def cancel_auth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return

    logger.info("Auth canceled telegram_id=%s", user.id)
    await redis_state.clear_state(user.id)
    await redis_state.clear_registration(user.id)
    await message.reply_text("Okay. You can sign up or sign in anytime.", reply_markup=build_start_keyboard())


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    query = update.callback_query
    if not query:
        return False

    data = query.data or ""
    if not data.startswith("auth:"):
        return False

    await query.answer()
    action = data.split(":", 1)[1]
    logger.info("Auth callback telegram_id=%s action=%s", query.from_user.id if query.from_user else "", action)
    if action == "signup":
        await start_signup(update, context)
        return True
    if action == "login":
        await start_login(update, context)
        return True
    if action == "cancel":
        await cancel_auth(update, context)
        return True
    return False


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return False

        state = await redis_state.get_state(user.id)
        logger.info("Auth state telegram_id=%s state=%s", user.id, state)
    if state == SIGNUP_FULL_NAME:
        full_name = message.text.strip()
        if len(full_name) < 3:
            await message.reply_text("Please enter your full name.", reply_markup=build_auth_keyboard())
            return True
        logger.info("Signup name captured telegram_id=%s", user.id)
        await redis_state.set_registration_field(user.id, "full_name", full_name)
        await redis_state.set_state(user.id, SIGNUP_EMAIL)
        await message.reply_text("Enter your email address.", reply_markup=build_auth_keyboard())
        return True

    if state == SIGNUP_EMAIL:
        email = message.text.strip()
        if not _is_email(email):
            await message.reply_text("Enter a valid email address.", reply_markup=build_auth_keyboard())
            return True
        logger.info("Signup email captured telegram_id=%s email=%s", user.id, _mask_email(email))
        await redis_state.set_registration_field(user.id, "email", email)
        await redis_state.set_state(user.id, SIGNUP_PHONE)
        await message.reply_text("Enter your Nigerian phone number.", reply_markup=build_auth_keyboard())
        return True

    if state == SIGNUP_PHONE:
        phone = message.text.strip()
        if not _is_nigerian_phone(phone):
            await message.reply_text("Enter a valid Nigerian phone number.", reply_markup=build_auth_keyboard())
            return True
        logger.info("Signup phone captured telegram_id=%s", user.id)
        await redis_state.set_registration_field(user.id, "phone", phone)
        await redis_state.set_state(user.id, SIGNUP_PASSWORD)
        await message.reply_text("Create a password with at least 8 characters.", reply_markup=build_auth_keyboard())
        return True

    if state == SIGNUP_PASSWORD:
        password = message.text.strip()
        if len(password) < 8:
            await message.reply_text("Password must be at least 8 characters.", reply_markup=build_auth_keyboard())
            return True

        full_name = await redis_state.get_registration_field(user.id, "full_name") or ""
        email = await redis_state.get_registration_field(user.id, "email") or ""
        phone = await redis_state.get_registration_field(user.id, "phone") or ""
        if not full_name or not email or not phone:
            await cancel_auth(update, context)
            return True

        logger.info("Signup submit telegram_id=%s email=%s", user.id, _mask_email(email))
        result, _cookies = await api_client.get_awaiting_otp_register(
            email=email,
            password=password,
            full_name=full_name,
            phone=phone,
        )
        if not result:
            logger.warning("Signup failed telegram_id=%s email=%s", user.id, _mask_email(email))
            await message.reply_text("I could not create your account. Please try again.", reply_markup=build_auth_keyboard())
            return True

        logger.info("Signup created telegram_id=%s email=%s", user.id, _mask_email(email))

        login_result, cookie_header = await api_client.login_user(email=email, password=password)
        if not login_result:
            logger.warning("Signup login failed telegram_id=%s email=%s", user.id, _mask_email(email))
            await message.reply_text("Account created, but login failed. Please sign in to continue.", reply_markup=build_auth_keyboard())
            return True

        logger.info("Signup login success telegram_id=%s email=%s", user.id, _mask_email(email))

        if cookie_header:
            await redis_state.set_auth_cookies(user.id, cookie_header)

        await redis_state.clear_state(user.id)
        await redis_state.clear_registration(user.id)

        account = await api_client.get_user_bank_account(cookies=cookie_header or "") if cookie_header else None
        if account:
            details = formatters.format_account_details(account)
        else:
            details = "Account created. Your virtual account is provisioning in the background. You can browse vendors now."

        await message.reply_text(details, reply_markup=build_main_menu())
        return True

    if state == LOGIN_EMAIL:
        email = message.text.strip()
        if not _is_email(email):
            await message.reply_text("Enter a valid email address.", reply_markup=build_auth_keyboard())
            return True
        logger.info("Login email captured telegram_id=%s email=%s", user.id, _mask_email(email))
        await redis_state.set_registration_field(user.id, "email", email)
        await redis_state.set_state(user.id, LOGIN_PASSWORD)
        await message.reply_text("Enter your password.", reply_markup=build_auth_keyboard())
        return True

    if state == LOGIN_PASSWORD:
        email = await redis_state.get_registration_field(user.id, "email") or ""
        password = message.text.strip()
        if not email:
            await cancel_auth(update, context)
            return True

        logger.info("Login submit telegram_id=%s email=%s", user.id, _mask_email(email))
        login_result, cookie_header = await api_client.login_user(email=email, password=password)
        if not login_result:
            logger.warning("Login failed telegram_id=%s email=%s", user.id, _mask_email(email))
            await message.reply_text("Login failed. Check your credentials and try again.", reply_markup=build_auth_keyboard())
            return True

        logger.info("Login success telegram_id=%s email=%s", user.id, _mask_email(email))

        if cookie_header:
            await redis_state.set_auth_cookies(user.id, cookie_header)

        await redis_state.clear_state(user.id)
        await redis_state.clear_registration(user.id)

        account = await api_client.get_user_bank_account(cookies=cookie_header or "") if cookie_header else None
        if account:
            text = formatters.format_account_details(account)
        else:
            text = "You are signed in. Use the menu to browse vendors or view your wallet."
        await message.reply_text(text, reply_markup=build_main_menu())
        return True

    return False


async def prompt_auth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message:
        return

    await message.reply_text("Sign up or sign in to continue.", reply_markup=build_auth_keyboard())
