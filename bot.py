# bot.py
import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

sys.path.append(str(Path(__file__).parent))

from config import settings
from handlers import router
from ai_client import GroqClient
from admin_panel import admin

# پیکربندی لاگینگ
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main():
    """
    تابع اصلی برای راه‌اندازی و اجرای ربات.
    """
    logger.info("Starting Alex VPN AI Assistant Bot...")
    
    if not settings.BOT_TOKEN or not settings.GROQ_API_KEY:
        logger.critical("BOT_TOKEN or GROQ_API_KEY is not set in environment variables. Exiting.")
        return

    admin.log_event("bot_start", "ربات شروع به کار کرد")

    groq_client = GroqClient(api_key=settings.GROQ_API_KEY)
    
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    dp.include_router(router)
    
    dp["groq_client"] = groq_client
    dp["admin_id"] = settings.ADMIN_ID
    
    try:
        logger.info("Bot is polling for updates...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Bot polling failed: {e}", exc_info=True)
        admin.log_event("error", f"خطای polling: {str(e)[:100]}")
    finally:
        admin.log_event("bot_stop", "ربات متوقف شد")
        await bot.session.close()
        logger.info("Bot session closed.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped manually via KeyboardInterrupt.")
        admin.log_event("bot_stop", "ربات دستی متوقف شد")
    except Exception as e:
        logger.critical(f"Unexpected error: {e}", exc_info=True)
