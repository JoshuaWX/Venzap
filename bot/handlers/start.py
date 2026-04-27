from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from bot.keyboards.order_keyboard import build_main_menu


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message:
        return

    text = (
        "Welcome to Venzap.\n"
        "Order from local vendors right here on Telegram."
    )
    await message.reply_text(text, reply_markup=build_main_menu())
