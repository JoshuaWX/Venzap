from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from bot.keyboards.order_keyboard import build_main_menu


async def prompt_auth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message:
        return

    text = "To sign in, use the Venzap web dashboard or the Telegram login flow."
    await message.reply_text(text, reply_markup=build_main_menu())
