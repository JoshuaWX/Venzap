from __future__ import annotations

import asyncio
import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.handlers import auth as auth_handler
from bot.handlers import rule_engine
from bot.keyboards.order_keyboard import build_main_menu
from bot.services.ai_client import parse_intent
from bot.state import redis_state


logger = logging.getLogger("venzap.bot.router")

RULE_ENGINE_ONLY_STATES = {
    "AWAIT_PASSWORD",
    "AWAIT_OTP",
    "CONFIRM_ORDER",
    "AWAIT_AMOUNT",
    "PROCESS_PAYMENT",
    "AWAIT_NEW_PASSWORD",
}


async def route_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user:
        return

    if update.callback_query:
        try:
            if await auth_handler.handle_callback(update, context):
                return
            await rule_engine.handle_callback(update, context)
        except Exception:
            logger.exception("Callback handling failed")
            try:
                await update.callback_query.answer("Something went wrong. Please try again.", show_alert=True)
            except Exception:
                pass
        return

    message = update.effective_message
    if not message or not message.text:
        return

    if await auth_handler.handle_text(update, context):
        return

    current_state = await redis_state.get_state(user.id)
    if current_state in RULE_ENGINE_ONLY_STATES:
        await rule_engine.handle(update, context)
        return

    selected_vendor = await redis_state.get_selected_vendor(user.id)
    cart_items = await redis_state.get_cart(user.id)

    try:
        result = await asyncio.wait_for(
            parse_intent(
                message.text,
                telegram_id=user.id,
                current_step=current_state,
                selected_vendor_name=selected_vendor,
                cart_items=cart_items,
            ),
            timeout=5.0,
        )
    except asyncio.TimeoutError:
        await fallback_handler(update, context)
        return
    except Exception:
        logger.exception("AI parse failed")
        await fallback_handler(update, context)
        return

    if result.is_valid and result.data:
        await rule_engine.handle_intent(result.data, update, context)
        return

    await fallback_handler(update, context)


async def fallback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message:
        return
    text = (
        "I did not quite get that. Here is what I can help with:\n"
        "- Browse vendors\n"
        "- View cart\n"
        "- Wallet\n"
        "- Orders\n"
        "- Help"
    )
    await message.reply_text(text, reply_markup=build_main_menu())
