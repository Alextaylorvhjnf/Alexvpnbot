import logging, asyncio
from pathlib import Path
from collections import defaultdict
from groq import AsyncGroq, APIError, APIConnectionError, RateLimitError, APITimeoutError

logger = logging.getLogger(__name__)

class GroqClient:
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.client = AsyncGroq(api_key=api_key)
        self.model = model
        self.system_prompt = self._load_prompt()
        self.history = defaultdict(list)

    def _load_prompt(self):
        p = Path("prompt.txt")
        return p.read_text(encoding="utf-8").strip() if p.exists() else "You are a helpful assistant."

    async def get_response(self, user_id: int, msg: str) -> str:
        if not msg or not msg.strip():
            return "پیامت خالیه! 😊"
        history = self.history[user_id]
        history.append({"role": "user", "content": msg})
        if len(history) > 10: history = history[-10:]
        messages = [{"role": "system", "content": self.system_prompt}] + history
        for attempt in range(2):
            try:
                r = await self.client.chat.completions.create(
                    messages=messages, model=self.model,
                    temperature=0.5, max_tokens=600, top_p=0.9, timeout=25.0
                )
                if r.choices and r.choices[0].message.content:
                    resp = r.choices[0].message.content.strip()
                    history.append({"role": "assistant", "content": resp})
                    if len(history) > 10: history = history[-10:]
                    self.history[user_id] = history
                    return resp
                return "نتونستم جواب بدم 😊"
            except RateLimitError:
                if attempt == 1: return "⏳ شلوغه! صبر کن 😊"
                await asyncio.sleep(2)
            except (APITimeoutError, asyncio.TimeoutError):
                if attempt == 1: return "⏰ طول کشید! 😊"
                await asyncio.sleep(1)
            except APIConnectionError:
                if attempt == 1: return "📡 مشکل اینترنت 😊"
                await asyncio.sleep(2)
            except APIError:
                return "🚨 خطای سرور 🆘 @Alexvpnsupport"
            except Exception as e:
                logger.error(f"Error: {e}")
                return "مشکلی پیش اومد 😊"
        return "نتونستم 😊"
