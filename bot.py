# bot.py
import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# افزودن مسیر پروژه به sys.path برای import راحت‌تر ماژول‌ها
sys.path.append(str(Path(__file__).parent))

from config import settings
from handlers import router
from ai_client import GroqClient

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
    
    # بررسی وجود تنظیمات ضروری
    if not settings.BOT_TOKEN or not settings.GROQ_API_KEY:
        logger.critical("BOT_TOKEN or GROQ_API_KEY is not set in environment variables. Exiting.")
        return

    # نمونه‌سازی از Groq Client
    groq_client = GroqClient(api_key=settings.GROQ_API_KEY)
    
    # راه‌اندازی ربات و Dispatcher
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # اضافه کردن router هندلرها
    dp.include_router(router)
    
    # تزریق وابستگی‌ها (مانند groq_client) به هندلرها
    # همچنین شناسه ادمین نیز برای دسترسی در هندلرها قرار می‌گیرد
    dp["groq_client"] = groq_client
    dp["admin_id"] = settings.ADMIN_ID
    
    try:
        logger.info("Bot is polling for updates...")
        # شروع دریافت و پردازش آپدیت‌ها
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Bot polling failed: {e}", exc_info=True)
    finally:
        await bot.session.close()
        logger.info("Bot session closed.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped manually via KeyboardInterrupt.")
    except Exception as e:
        logger.critical(f"Unexpected error: {e}", exc_info=True)
