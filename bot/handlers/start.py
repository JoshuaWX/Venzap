from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from bot.keyboards.auth_keyboard import build_start_keyboard


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message:
        return

    text = (
        "Welcome to Venzap.\n"
        "Sign up or sign in to browse vendors, fund your wallet, and place orders."
    )
    await message.reply_text(text, reply_markup=build_start_keyboard())
