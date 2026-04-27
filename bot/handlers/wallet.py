from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from bot.keyboards.order_keyboard import build_main_menu


async def show_wallet_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    message_override: str | None = None,
) -> None:
    message = update.effective_message
    if not message:
        return

    text = message_override or "Wallet actions are available from your account menu."
    await message.reply_text(text, reply_markup=build_main_menu())
