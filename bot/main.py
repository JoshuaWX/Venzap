from __future__ import annotations

import logging
import signal
import sys

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
    
    # Handle graceful shutdown on SIGTERM/SIGINT
    def sig_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        # Stop polling
        application.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    
    # Use idle() to block until shutdown signal is received
    application.run_polling(close_loop=False, allowed_updates=[])


if __name__ == "__main__":
    main()
