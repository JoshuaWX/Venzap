from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from bot.keyboards.order_keyboard import build_main_menu
from bot.services import api_client
from bot.utils import formatters


async def show_order_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    message_override: str | None = None,
    latest_only: bool = False,
) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return

    if message_override:
        await message.reply_text(message_override, reply_markup=build_main_menu())
        return

    orders = await api_client.get_order_history(user.id)
    if not orders:
        await message.reply_text("You have no orders yet.", reply_markup=build_main_menu())
        return

    if latest_only:
        text = formatters.format_order_status(orders[0])
    else:
        text = formatters.format_order_history(orders)

    await message.reply_text(text, reply_markup=build_main_menu())
