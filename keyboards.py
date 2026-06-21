from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📱 راهنمای نصب"),
        KeyboardButton(text="🔗 آموزش لینک اشتراک")
    )
    builder.row(
        KeyboardButton(text="🔄 بروزرسانی و رفع مشکل"),
        KeyboardButton(text="🛠️ عیب‌یابی تعاملی")
    )
    builder.row(
        KeyboardButton(text="📥 دانلود برنامه‌ها"),
        KeyboardButton(text="📚 آموزش اتصال برنامه‌ها")
    )
    builder.row(
        KeyboardButton(text="🔍 تست کانفیگ"),
        KeyboardButton(text="🚀 تست سرعت اینترنت")
    )
    builder.row(
        KeyboardButton(text="💬 گفتگو با الکس"),
        KeyboardButton(text="🛍️ خرید اشتراک")
    )
    builder.row(KeyboardButton(text="🆘 پشتیبانی"))
    return builder.as_markup(resize_keyboard=True)

def get_chat_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="🏠 بازگشت به منوی اصلی"))
    return builder.as_markup(resize_keyboard=True)

def get_troubleshoot_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="🔙 پایان عیب‌یابی"))
    return builder.as_markup(resize_keyboard=True)

def get_back_to_main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🏠 بازگشت به منوی اصلی", callback_data="menu_main"))
    return builder.as_markup()

def get_support_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🆘 پشتیبانی انسانی", url="https://t.me/Alexvpnsupport"))
    builder.row(InlineKeyboardButton(text="🛍️ خرید اشتراک", url="https://t.me/Alexvpn98bot"))
    return builder.as_markup()

def get_shop_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🛍️ رفتن به ربات فروش", url="https://t.me/Alexvpn98bot"))
    return builder.as_markup()

def get_apps_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🍏 HAPP", url="https://apps.apple.com/us/app/happ-proxy-utility/id6504287215"), InlineKeyboardButton(text="🍏 FoXray", url="https://apps.apple.com/kz/app/foxray-vpn-super-master/id6770070697"))
    builder.row(InlineKeyboardButton(text="🍏 Streisand", url="https://apps.apple.com/app/id6450534064"))
    builder.row(InlineKeyboardButton(text="🤖 V2rayNG", url="https://github.com/2dust/v2rayNG/releases/download/2.2.3/v2rayNG_2.2.3-fdroid_arm64-v8a.apk"), InlineKeyboardButton(text="🤖 V2rayNG Pro", url="https://github.com/2dust/v2rayNG/releases/download/2.2.5/v2rayNG_2.2.5-fdroid_arm64-v8a.apk"))
    builder.row(InlineKeyboardButton(text="🤖 Nekobox", url="https://github.com/MatsuriDayo/NekoBoxForAndroid/releases/download/1.4.2/NekoBox-1.4.2-arm64-v8a.apk"), InlineKeyboardButton(text="🤖 Hiddify", url="https://github.com/hiddify/hiddify-next/releases/latest"))
    builder.row(InlineKeyboardButton(text="💻 Nekoray", url="https://github.com/MatsuriDayo/nekoray/releases/download/4.0.1/nekoray-4.0.1-2024-12-12-windows64.zip"), InlineKeyboardButton(text="💻 Hiddify", url="https://github.com/hiddify/hiddify-next/releases/latest"))
    builder.row(InlineKeyboardButton(text="🏠 منوی اصلی", callback_data="menu_main"))
    return builder.as_markup()

def get_tutorials_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🍏 HAPP", callback_data="tutorial_happ"), InlineKeyboardButton(text="🍏 FoXray", callback_data="tutorial_foxray"))
    builder.row(InlineKeyboardButton(text="🍏 Streisand", callback_data="tutorial_streisand"))
    builder.row(InlineKeyboardButton(text="🤖 V2rayNG", callback_data="tutorial_v2rayng"), InlineKeyboardButton(text="🤖 Nekobox", callback_data="tutorial_nekobox"))
    builder.row(InlineKeyboardButton(text="🤖 Hiddify", callback_data="tutorial_hiddify"))
    builder.row(InlineKeyboardButton(text="💻 Nekoray", callback_data="tutorial_nekoray"), InlineKeyboardButton(text="💻 Hiddify", callback_data="tutorial_hiddify_win"))
    builder.row(InlineKeyboardButton(text="🏠 منوی اصلی", callback_data="menu_main"))
    return builder.as_markup()

def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📊 آمار کلی", callback_data="admin_stats"))
    builder.row(InlineKeyboardButton(text="👥 امروز", callback_data="admin_users_today"), InlineKeyboardButton(text="👥 دیروز", callback_data="admin_users_yesterday"))
    builder.row(InlineKeyboardButton(text="👥 هفته", callback_data="admin_users_week"), InlineKeyboardButton(text="👥 ماه", callback_data="admin_users_month"))
    builder.row(InlineKeyboardButton(text="👥 همه", callback_data="admin_users_all"))
    builder.row(InlineKeyboardButton(text="💬 چت امروز", callback_data="admin_chats_today"), InlineKeyboardButton(text="💬 دیروز", callback_data="admin_chats_yesterday"))
    builder.row(InlineKeyboardButton(text="📋 رویدادها", callback_data="admin_events_day"))
    builder.row(InlineKeyboardButton(text="🔥 فعال‌ترین", callback_data="admin_top_users"))
    builder.row(InlineKeyboardButton(text="📢 پیام همگانی", callback_data="admin_broadcast_prompt"))
    builder.row(InlineKeyboardButton(text="🔙 خروج", callback_data="admin_exit"))
    return builder.as_markup()

def get_admin_back_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 بازگشت به پنل", callback_data="admin_main"))
    return builder.as_markup()
