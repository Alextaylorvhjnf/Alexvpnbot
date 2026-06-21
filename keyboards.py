# keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_support_keyboard() -> InlineKeyboardMarkup:
    """
    ساخت اینلاین کیبورد برای ارتباط با پشتیبانی انسانی.
    """
    button = InlineKeyboardButton(
        text="📞 ارتباط با پشتیبانی",
        url="https://t.me/Alexvpnsupport"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
    return keyboard
