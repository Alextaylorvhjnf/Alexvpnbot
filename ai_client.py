# ai_client.py
import logging
import asyncio
from pathlib import Path
from groq import AsyncGroq, APIError, APIConnectionError, RateLimitError, APITimeoutError

logger = logging.getLogger(__name__)

class GroqClient:
    """
    کلاینت برای ارتباط با API GroqCloud با مدیریت خطا و Rate Limit و Timeout.
    """
    def __init__(self, api_key: str, model: str = "llama-3.1-70b-versatile"):
        if not api_key:
            raise ValueError("Groq API key cannot be empty.")
        self.client = AsyncGroq(api_key=api_key)
        self.model = model
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """
        بارگذاری prompt سیستم از فایل prompt.txt
        """
        prompt_path = Path("prompt.txt")
        if not prompt_path.exists():
            logger.error("prompt.txt not found. Using default empty system prompt.")
            return "You are a helpful assistant."
        
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt = f.read().strip()
            if not prompt:
                logger.warning("prompt.txt is empty. Using default system prompt.")
                return "You are a helpful assistant."
            return prompt

    async def get_response(self, user_message: str) -> str:
        """
        ارسال پیام کاربر به Groq API و دریافت پاسخ با مدیریت خطاهای کامل.
        """
        if not user_message or not user_message.strip():
            return "پیام ارسالی معتبر نیست. لطفاً دوباره تلاش کنید."

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message}
        ]

        max_retries = 3
        retry_delay = 2  # ثانیه

        for attempt in range(max_retries):
            try:
                # timeout=30 ثانیه تنظیم شده است
                chat_completion = await self.client.chat.completions.create(
                    messages=messages,
                    model=self.model,
                    timeout=30.0
                )
                
                if chat_completion.choices:
                    response_text = chat_completion.choices[0].message.content
                    if response_text:
                        return response_text.strip()
                    else:
                        logger.warning(f"Received empty content from Groq API on attempt {attempt+1}.")
                        return "متأسفانه پاسخی از سمت سرور دریافت نشد. لطفاً مجدداً تلاش کنید."
                else:
                    logger.warning(f"No choices returned from Groq API on attempt {attempt+1}.")
                    return "خطا در تولید پاسخ. لطفاً بعداً تلاش کنید."

            except RateLimitError as rle:
                logger.warning(f"Rate limit hit on attempt {attempt+1}: {rle}. Retrying in {retry_delay}s.")
                if attempt == max_retries - 1:
                    return "⏳ به دلیل درخواست‌های زیاد، موقتاً محدودیت ایجاد شده است. لطفاً چند لحظه دیگر تلاش کنید."
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff

            except (APITimeoutError, asyncio.TimeoutError) as te:
                logger.error(f"Timeout error on attempt {attempt+1}: {te}. Retrying in {retry_delay}s.")
                if attempt == max_retries - 1:
                    return "⌛ زمان پاسخگویی به پایان رسید. لطفاً دوباره تلاش کنید."
                await asyncio.sleep(retry_delay)
                retry_delay *= 2

            except APIConnectionError as ace:
                logger.error(f"Connection error on attempt {attempt+1}: {ace}. Retrying in {retry_delay}s.")
                if attempt == max_retries - 1:
                    return "📡 خطا در برقراری ارتباط با سرور. لطفاً اتصال اینترنت خود را بررسی کنید و دوباره تلاش نمایید."
                await asyncio.sleep(retry_delay)
                retry_delay *= 2

            except APIError as apie:
                logger.error(f"Groq API error on attempt {attempt+1}: {apie}", exc_info=True)
                return f"🚨 خطای سرویس هوش مصنوعی رخ داد. کد خطا: {getattr(apie, 'status_code', 'N/A')}. لطفاً با پشتیبانی تماس بگیرید."

            except Exception as e:
                logger.critical(f"Unexpected error in Groq client on attempt {attempt+1}: {e}", exc_info=True)
                return "🤖 یک خطای پیش‌بینی نشده در پردازش درخواست رخ داد. لطفاً بعداً تلاش کنید."

        return "پردازش با خطا مواجه شد. لطفاً دوباره تلاش کنید."
