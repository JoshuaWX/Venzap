from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from bot.keyboards.order_keyboard import build_main_menu


async def send_help(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    faq_answer: str | None = None,
) -> None:
    message = update.effective_message
    if not message:
        return

    if faq_answer:
        text = faq_answer
    else:
        text = (
            "Here is what I can help with:\n"
            "- Browse vendors\n"
            "- View cart\n"
            "- Wallet\n"
            "- Orders"
        )

    await message.reply_text(text, reply_markup=build_main_menu())
