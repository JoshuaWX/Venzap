from __future__ import annotations

import logging

from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from bot.config import settings
from bot.handlers.start import start_command
from bot.middleware.message_router import route_message


logger = logging.getLogger("venzap.bot")


def _build_application() -> Application:
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required")

    application = Application.builder().token(settings.telegram_bot_token).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(route_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, route_message))
    return application


def main() -> None:
    application = _build_application()
    logger.info("Starting Venzap bot")
    application.run_polling(close_loop=False)


if __name__ == "__main__":
    main()
