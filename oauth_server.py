#!/usr/bin/env python3
"""
Telegram Bot for Automated Blogger Posting
Main entry point for the application
"""

import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from bot_handlers import BotHandlers

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Start the bot"""
    # Get bot token from environment variables
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "8380633057:AAGHjxspKX8Sywp1x2euJfMaJOMkbrJ-YmA")

    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        return

    # Create application
    application = Application.builder().token(bot_token).build()

    # Initialize bot handlers
    handlers = BotHandlers()

    # Add command handlers
    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CommandHandler("post", handlers.post_command))
    application.add_handler(CommandHandler("cancel", handlers.cancel_command))
    application.add_handler(CommandHandler("edit", handlers.edit_command))
    application.add_handler(CommandHandler("help", handlers.help_command))
    application.add_handler(CommandHandler("status", handlers.status_command))
    application.add_handler(CommandHandler("template", handlers.template_command))
    application.add_handler(CommandHandler("auth", handlers.auth_command))
    application.add_handler(CommandHandler("complete_auth", handlers.complete_auth_command))
    application.add_handler(CommandHandler("manual_auth", handlers.manual_auth_command))

    # Add callback query handler for buttons
    application.add_handler(CallbackQueryHandler(handlers.button_callback))

    # Add message handler for text inputs
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_text))

    # Start the bot
    logger.info("Starting Blogger Bot...")
    application.run_polling()

if __name__ == '__main__':
    main()
