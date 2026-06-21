import logging

logger = logging.getLogger(__name__)

async def send_telegram_notification(bot, chat_id: int):
    try:
        await bot.send_message(chat_id=chat_id, text="✨", disable_notification=False)
    except Exception as e:
        logger.error(f"Notify error: {e}")
