# handlers.py
import logging
import asyncio
from typing import Dict, Any

from aiogram import Router, types, Bot
from aiogram.filters import CommandStart, Command
from aiogram.enums import ChatType

from ai_client import GroqClient
from keyboards import get_support_keyboard

logger = logging.getLogger(__name__)
router = Router()

# عبارات کلیدی که نشان‌دهنده نیاز به پشتیبانی انسانی هستند
HUMAN_SUPPORT_TRIGGERS = [
    "نیاز به بررسی پشتیبانی انسانی",
    "پشتیبانی انسانی",
    "برای بررسی دقیق‌تر نیاز به بررسی پشتیبانی انسانی وجود دارد",
    "بررسی پشتیبانی انسانی"
]

def check_for_human_support(response_text: str) -> bool:
    """
    بررسی می‌کند که آیا پاسخ هوش مصنوعی نیاز به دخالت انسان دارد یا خیر.
    """
    if not response_text:
        return False
    for trigger in HUMAN_SUPPORT_TRIGGERS:
        if trigger in response_text:
            return True
    return False

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    """
    هندلر دستور /start . فقط در پیام خصوصی پاسخ می‌دهد.
    """
    if message.chat.type != ChatType.PRIVATE:
        return  # در گروه‌ها پاسخی به /start نمی‌دهد مگر اینکه خواسته باشید

    user_name = message.from_user.full_name
    welcome_text = (
        f"سلام {user_name} عزیز! \n"
        f"من **Alex VPN AI Assistant** هستم، دستیار هوشمند پشتیبانی فروشگاه VPN.\n\n"
        f"چطور می‌توانم به شما کمک کنم؟ لطفاً مشکل یا سوال خود را به فارسی یا انگلیسی بفرمایید."
    )
    await message.answer(welcome_text, parse_mode="Markdown")

@router.message()
async def handle_user_message(message: types.Message, bot: Bot, groq_client: GroqClient):
    """
    هندلر اصلی برای پردازش تمامی پیام‌های متنی کاربران در چت خصوصی.
    از پردازش پیام‌های گروه‌ها و کانال‌ها صرف‌نظر می‌کند.
    """
    # فقط در چت خصوصی پاسخ می‌دهد
    if message.chat.type != ChatType.PRIVATE:
        return

    if not message.text:
        # پیام‌های غیر متنی (مثل عکس، استیکر و ...) را نادیده بگیرید یا پاسخ دهید
        await message.reply("لطفاً سوال خود را به صورت متن ارسال کنید.")
        return

    user_message = message.text.strip()
    if not user_message:
        await message.reply("پیام شما خالی است. لطفاً مجدداً تلاش کنید.")
        return

    # ارسال وضعیت تایپ برای بهبود تجربه کاربری
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        # دریافت پاسخ از Groq API
        ai_response = await groq_client.get_response(user_message)
        
        # بررسی نیاز به پشتیبانی انسانی
        if check_for_human_support(ai_response):
            # ارسال پاسخ هوش مصنوعی
            await message.reply(ai_response)
            # ارسال پیام جداگانه با دکمه پشتیبانی
            await message.answer(
                "⚠️ برای بررسی دقیق‌تر لطفاً با پشتیبانی انسانی تماس بگیرید:",
                reply_markup=get_support_keyboard()
            )
        else:
            # ارسال پاسخ عادی هوش مصنوعی
            # تلگرام محدودیت 4096 کاراکتری دارد، پاسخ‌های خیلی طولانی را می‌شکنیم
            if len(ai_response) > 4000:
                for x in range(0, len(ai_response), 4000):
                    await message.reply(ai_response[x:x+4000])
            else:
                await message.reply(ai_response)

    except Exception as e:
        logger.error(f"Error handling message from user {message.from_user.id}: {e}", exc_info=True)
        error_text = (
            "❌ متأسفانه در پردازش درخواست شما خطایی رخ داد. لطفاً بعداً تلاش کنید.\n"
            "اگر مشکل تکرار شد، با پشتیبانی در میان بگذارید."
        )
        await message.reply(error_text, reply_markup=get_support_keyboard())

# --- مدیریت خطاهای داخلی تلگرام (اختیاری) ---
@router.error()
async def error_handler(event: types.ErrorEvent):
    """
    مدیریت خطاهای ناشی از polling و آپدیت‌ها.
    """
    logger.critical(f"Update processing error: {event.exception}", exc_info=True)
    # می‌توانید اینجا به ادمین اطلاع دهید
