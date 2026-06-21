# config.py
import os
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()

class Settings:
    """
    کلاس نگهداری تنظیمات ربات که مقادیر را از متغیرهای محیطی می‌خواند.
    """
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0"))
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

settings = Settings()
