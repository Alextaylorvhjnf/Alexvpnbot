import logging, asyncio, sys
from datetime import datetime
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from aiogram import Router, types, Bot, F
from aiogram.filters import CommandStart, Command
from aiogram.enums import ChatType
from ai_client import GroqClient
from keyboards import *
from admin_panel import admin
from notify_helper import send_telegram_notification
from config_tester import ConfigTester
from config import settings

logger = logging.getLogger(__name__)
router = Router()
ADMIN_ID = settings.ADMIN_ID

HUMAN_SUPPORT_TRIGGERS = ["نیاز به بررسی پشتیبانی انسانی", "پشتیبانی انسانی"]
SHOP_TRIGGERS = ["خرید", "اشتراک", "تست", "قیمت", "تمدید", "افزایش حجم", "شارژ", "buy", "subscribe", "plan", "پلن", "تعرفه", "هزینه", "پرداخت"]
user_free_chat_mode = {}
user_troubleshoot_mode = {}
user_config_test_mode = {}
admin_broadcast_mode = {}

def check_for_human_support(text): return any(t in text for t in HUMAN_SUPPORT_TRIGGERS) if text else False
def check_for_shop_intent(text): return any(t in text.lower() for t in SHOP_TRIGGERS) if text else False
def is_admin(uid): return uid == ADMIN_ID
def is_config(text): return any(text.startswith(p) for p in ["vless://","vmess://","trojan://","ss://","ssr://"]) or ("://" in text and "subscribe" in text.lower())

async def reply_with_sound(msg, bot, text, **kw):
    m = await msg.reply(text, **kw)
    try: await send_telegram_notification(bot, msg.chat.id)
    except: pass
    return m

# ADMIN - بدون تغییر
@router.message(Command("admin"))
async def cmd_admin(message: types.Message, bot: Bot):
    if not is_admin(message.from_user.id): return
    s = admin.get_stats()
    t = f"🔐 **پنل مدیریت**\n\n👥 کل: `{s['total_users']}` | امروز: `{s['today_users']}`\n💬 مکالمات امروز: `{s['today_chats']}`\n🕐 `{datetime.now().strftime('%H:%M')}`"
    await message.answer(t, parse_mode="Markdown", reply_markup=get_admin_main_keyboard())

@router.callback_query(F.data == "admin_main")
async def cb_am(c: types.CallbackQuery):
    if not is_admin(c.from_user.id): return
    s = admin.get_stats()
    await c.message.edit_text(f"🔐 **پنل**\n👥 `{s['total_users']}` | 💬 `{s['today_chats']}`", parse_mode="Markdown", reply_markup=get_admin_main_keyboard())
    await c.answer()

@router.callback_query(F.data == "admin_stats")
async def cb_as(c: types.CallbackQuery):
    if not is_admin(c.from_user.id): return
    s = admin.get_stats()
    t = f"📊 کل: `{s['total_users']}` | امروز: `{s['today_users']}` | دیروز: `{s['yesterday_users']}`\n💬 کل: `{s['total_chats']}` | امروز: `{s['today_chats']}`"
    await c.message.edit_text(t, parse_mode="Markdown", reply_markup=get_admin_back_keyboard())
    await c.answer()

for period, label in [("today","امروز"),("yesterday","دیروز"),("week","هفته"),("month","ماه"),("all","همه")]:
    async def show_users(c: types.CallbackQuery, p=period, l=label):
        if not is_admin(c.from_user.id): return
        users = admin.get_users_by_period(p)
        t = f"👥 **{l}** ({len(users)})\n\n" if users else f"👥 **{l}** خالی"
        if users:
            for i,u in enumerate(users[-15:],1): t += f"{i}. `{u['user_id']}` - {u.get('full_name','؟')[:20]}\n"
        await c.message.edit_text(t, parse_mode="Markdown", reply_markup=get_admin_back_keyboard())
        await c.answer()
    router.callback_query(F.data == f"admin_users_{period}")(show_users)

for period, label in [("today","امروز"),("yesterday","دیروز"),("week","هفته"),("month","ماه")]:
    async def show_chats(c: types.CallbackQuery, p=period, l=label):
        if not is_admin(c.from_user.id): return
        chats = admin.get_chats_by_period(p, 10)
        t = f"💬 **{l}** ({len(chats)})\n\n" if chats else f"💬 **{l}** خالی"
        if chats:
            for i,ch in enumerate(chats,1): t += f"{i}. 👤 `{ch.get('user_id')}`: {ch.get('user_message','')[:50]}...\n"
        await c.message.edit_text(t, parse_mode="Markdown", reply_markup=get_admin_back_keyboard())
        await c.answer()
    router.callback_query(F.data == f"admin_chats_{period}")(show_chats)

for period, label in [("day","۲۴h"),("week","هفته")]:
    async def show_events(c: types.CallbackQuery, p=period, l=label):
        if not is_admin(c.from_user.id): return
        ev = admin.get_events_by_period(p)
        t = f"📋 **{l}** ({len(ev)})\n\n" if ev else f"📋 **{l}** خالی"
        if ev:
            for i,e in enumerate(ev[:15],1): t += f"{i}. {e.get('description','')[:70]}\n"
        await c.message.edit_text(t, parse_mode="Markdown", reply_markup=get_admin_back_keyboard())
        await c.answer()
    router.callback_query(F.data == f"admin_events_{period}")(show_events)

@router.callback_query(F.data == "admin_top_users")
async def cb_top(c: types.CallbackQuery):
    if not is_admin(c.from_user.id): return
    top = admin.get_top_users("week",10)
    t = "🔥 **فعال‌ترین**\n\n" if top else "🔥 خالی"
    if top:
        for i,u in enumerate(top,1): t += f"{'🥇' if i==1 else '🥈' if i==2 else '🥉' if i==3 else f'{i}.'} `{u['user_id']}` - {u.get('full_name','؟')[:20]} | 💬 {u['count']}\n"
    await c.message.edit_text(t, parse_mode="Markdown", reply_markup=get_admin_back_keyboard())
    await c.answer()

@router.callback_query(F.data == "admin_broadcast_prompt")
async def cb_bp(c: types.CallbackQuery):
    if not is_admin(c.from_user.id): return
    admin_broadcast_mode[c.from_user.id] = True
    await c.message.edit_text("📢 پیام رو تایپ کن:", reply_markup=get_admin_back_keyboard())
    await c.answer()

@router.callback_query(F.data == "admin_exit")
async def cb_ex(c: types.CallbackQuery):
    await c.message.edit_text("🔒 خارج شدی", reply_markup=None)
    await c.answer()

# ==================== USER ====================

@router.message(CommandStart())
async def cmd_start(m: types.Message, bot: Bot):
    if m.chat.type != ChatType.PRIVATE: return
    admin.add_user(m.from_user.id, m.from_user.username or "", m.from_user.full_name)
    user_free_chat_mode[m.from_user.id] = False
    user_troubleshoot_mode[m.from_user.id] = False
    t = f"🌟 **سلام {m.from_user.full_name} عزیز!** 🥰\n\nمن **الکس** هستم، پشتیبان VPN شما!\nاز منوی زیر استفاده کن 👇"
    await m.answer(t, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())

@router.message(Command("menu"))
async def cmd_menu(m: types.Message, bot: Bot):
    if m.chat.type != ChatType.PRIVATE: return
    user_free_chat_mode[m.from_user.id] = False
    user_troubleshoot_mode[m.from_user.id] = False
    await m.answer("🏠 **منوی اصلی**", parse_mode="Markdown", reply_markup=get_main_menu_keyboard())

# ==================== BUTTON HANDLERS ====================

@router.message(F.text == "📱 راهنمای نصب")
async def btn_install(m: types.Message, bot: Bot):
    t = (
        "📱 **راهنمای کامل نصب VPN**\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "**۱. انتخاب و دانلود برنامه**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "از منوی 📥 دانلود برنامه‌ها، برنامه مناسب دستگاهت رو انتخاب کن:\n\n"
        "🍏 **آیفون:** HAPP, FoXray, Streisand\n"
        "🤖 **اندروید:** V2rayNG, Nekobox, Hiddify\n"
        "💻 **ویندوز:** Nekoray, Hiddify\n\n"
        "⛔ فقط از لینک‌های خود ربات دانلود کن!\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "**۲. نصب برنامه**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "• **اندروید:** فایل APK رو باز کن → Install → Allow Unknown Sources\n"
        "• **آیفون:** از اپ استور نصب کن (معمولی)\n"
        "• **ویندوز:** فایل exe یا zip رو اجرا کن\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "**۳. وارد کردن لینک اشتراک**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "۱. لینک اشتراک رو کپی کن\n"
        "۲. برنامه رو باز کن\n"
        "۳. روی ➕ (بالا) بزن\n"
        "۴. گزینه Subscribe یا Add From Clipboard\n"
        "۵. لینک رو Paste کن و OK بزن\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "**۴. بروزرسانی**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "• برو به Subscription\n"
        "• Update Subscription رو بزن\n"
        "• صبر کن تا کانفیگ‌ها لود بشن\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "**۵. اتصال**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "• یه کانفیگ انتخاب کن\n"
        "• Connect بزن ✅\n\n"
        "💡 آموزش دقیق هر برنامه در 📚 آموزش اتصال برنامه‌ها\n\n"
        "🛍️ @Alexvpn98bot | 🆘 @Alexvpnsupport"
    )
    await m.answer(t, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())

@router.message(F.text == "🔗 آموزش لینک اشتراک")
async def btn_sub(m: types.Message, bot: Bot):
    t = (
        "🔗 **آموزش کامل لینک اشتراک**\n\n"
        "لینک اشتراک یه URL مخصوصه که کانفیگ‌ها رو توی برنامه VPN مدیریت میکنه.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📱 **آموزش در هر برنامه:**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "**V2rayNG (اندروید):**\n"
        "۱. ➕ (بالا) → Subscribe\n"
        "۲. URL: Paste کن\n"
        "۳. Remarks: Alex VPN\n"
        "۴. OK → تب Subscription → ↻ Update\n\n"
        "**HAPP (آیفون):**\n"
        "۱. ➕ → Add From Clipboard\n"
        "۲. Subscription → Update Subscription\n\n"
        "**Nekobox (اندروید):**\n"
        "۱. Menu → Subscriptions → ➕\n"
        "۲. Paste → OK → Update\n\n"
        "**Streisand (آیفون):**\n"
        "۱. Subscriptions → ➕ → Paste → Save\n\n"
        "**Hiddify:**\n"
        "۱. Subscriptions → Add → Paste → Save → Update All\n\n"
        "**Nekoray (ویندوز):**\n"
        "۱. Server → Add Subscription → Paste → OK\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🔄 **کی باید آپدیت کنم؟**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "• وقتی VPN وصل نمیشه\n"
        "• هر ۴-۶ ساعت\n"
        "• وقتی کانفیگ جدید اومده\n"
        "• وقتی سرعت پایینه\n\n"
        "🛍️ @Alexvpn98bot | 🆘 @Alexvpnsupport"
    )
    await m.answer(t, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())

@router.message(F.text == "🔄 بروزرسانی و رفع مشکل")
async def btn_restart(m: types.Message, bot: Bot):
    t = (
        "🔄 **بروزرسانی و رفع مشکل اتصال**\n\n"
        "اگه VPN وصل نمیشه، این مراحل رو **دقیقاً به همین ترتیب** انجام بده:\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "**قدم ۱: برنامه رو کامل ببند**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "• اندروید: Settings → Apps → [VPN] → Force Stop\n"
        "• آیفون: انگشت از پایین بکش بالا → برنامه رو ببند\n"
        "• ویندوز: Task Manager → End Task\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "**قدم ۲: اینترنت رو ریست کن**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "• Airplane Mode رو ۱۰ ثانیه روشن کن\n"
        "• خاموش کن و صبر کن وصل بشه\n"
        "• WiFi رو یه بار خاموش و روشن کن\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "**قدم ۳: برنامه رو باز کن**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "**قدم ۴: اشتراک رو آپدیت کن (مهم‌ترین قدم!)**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "• برو به بخش Subscription\n"
        "• روی Update Subscription یا ↻ بزن\n"
        "• **صبر کن!** ممکنه ۱۰-۶۰ ثانیه طول بکشه\n"
        "• پیغام Success = کانفیگ‌ها آماده‌ان\n"
        "• اگه خطا گرفتی، دوباره Update رو بزن\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "**قدم ۵: Ping بگیر**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "• چندتا کانفیگ رو انتخاب کن\n"
        "• دکمه Ping یا Test رو بزن\n"
        "• عدد کمتر = سریع‌تر\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "**قدم ۶: وصل شو**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "• کانفیگ با Ping کم ← Connect\n"
        "• تست کن با باز کردن یه سایت\n"
        "• نشد ← کانفیگ بعدی\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "**قدم ۷: راه آخر**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "• برنامه رو کامل حذف کن\n"
        "• از 📥 دانلود، آخرین نسخه رو نصب کن\n"
        "• لینک اشتراک رو دوباره وارد کن\n\n"
        "💡 ۹۰٪ مشکلات با آپدیت اشتراک حل میشه!\n\n"
        "🛍️ @Alexvpn98bot | 🆘 @Alexvpnsupport"
    )
    await m.answer(t, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())

@router.message(F.text == "🛠️ عیب‌یابی تعاملی")
async def btn_trouble(m: types.Message, bot: Bot):
    user_troubleshoot_mode[m.from_user.id] = True
    t = (
        "🛠️ **عیب‌یابی تعاملی**\n\n"
        "من قدم به قدم کمکت می‌کنم مشکلت رو پیدا کنی!\n\n"
        "لطفاً بگو دقیقاً چه مشکلی داری:\n\n"
        "۱. 📱 **صفحه سفید میاد / سایت باز نمیشه**\n"
        "۲. ⏰ **خطای Timeout یا Connection Refused**\n"
        "۳. 📡 **قطع و وصل مکرر**\n"
        "۴. 🐌 **سرعت پایینه**\n"
        "۵. 💥 **برنامه کرش میکنه**\n"
        "۶. ❌ **خطای دیگه**\n\n"
        "یا مشکلت رو به صورت کامل توضیح بده 👇\n\n"
        "برای پایان: 🔙 پایان عیب‌یابی"
    )
    await m.answer(t, parse_mode="Markdown", reply_markup=get_troubleshoot_keyboard())

@router.message(F.text == "🔙 پایان عیب‌یابی")
async def btn_trouble_end(m: types.Message, bot: Bot):
    user_troubleshoot_mode[m.from_user.id] = False
    await m.answer("✅ عیب‌یابی تموم شد. برگشتی به منوی اصلی 😊", reply_markup=get_main_menu_keyboard())

@router.message(F.text == "📥 دانلود برنامه‌ها")
async def btn_apps(m: types.Message, bot: Bot):
    t = (
        "📥 **دانلود برنامه‌های VPN (لینک مستقیم)**\n\n"
        "⛔ **هشدار امنیتی:** فقط از لینک‌های زیر دانلود کن!\n"
        "نسخه‌های جعلی ممکنه اطلاعاتت رو بدزدن!\n\n"
        "روی اسم برنامه کلیک کن 👇\n\n"
        "🛍️ @Alexvpn98bot | 🆘 @Alexvpnsupport"
    )
    await m.answer(t, parse_mode="Markdown", reply_markup=get_apps_keyboard())

@router.message(F.text == "📚 آموزش اتصال برنامه‌ها")
async def btn_tutorials(m: types.Message, bot: Bot):
    t = (
        "📚 **آموزش اتصال به تفکیک برنامه**\n\n"
        "برای هر برنامه، آموزش کامل و قدم به قدم داریم!\n"
        "روی برنامه‌ای که داری کلیک کن 👇\n\n"
        "🛍️ @Alexvpn98bot | 🆘 @Alexvpnsupport"
    )
    await m.answer(t, parse_mode="Markdown", reply_markup=get_tutorials_keyboard())

@router.message(F.text == "🔍 تست کانفیگ")
async def btn_test_config(m: types.Message, bot: Bot):
    user_config_test_mode[m.from_user.id] = True
    t = (
        "🔍 **تست کانفیگ**\n\n"
        "کانفیگ یا لینک اشتراکت رو بفرست تا برات تست کنم!\n\n"
        "✅ کانفیگ‌های قابل تست:\n"
        "• VLESS\n• VMess\n• Trojan\n• Shadowsocks\n\n"
        "🔗 لینک اشتراک رو هم می‌تونم بررسی کنم.\n\n"
        "📌 کافیه کانفیگ رو کپی کنی و بفرستی!\n\n"
        "برای برگشت: /menu"
    )
    await m.answer(t, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())

@router.message(F.text == "💬 گفتگو با الکس")
async def btn_free(m: types.Message, bot: Bot):
    user_free_chat_mode[m.from_user.id] = True
    t = (
        "💬 **گفتگوی آزاد با الکس** 🥰\n\n"
        "حالا می‌تونی هر سوالی داری مستقیماً از من بپرسی!\n"
        "درباره VPN، اینترنت، مشکلات فنی، یا هر چیز دیگه...\n\n"
        "🗣️ سوالت رو بنویس، من اینجام!\n\n"
        "برای برگشت به منو، دکمه زیر رو بزن 👇"
    )
    await m.answer(t, parse_mode="Markdown", reply_markup=get_chat_keyboard())

@router.message(F.text == "🏠 بازگشت به منوی اصلی")
async def btn_back_to_main(m: types.Message, bot: Bot):
    user_free_chat_mode[m.from_user.id] = False
    user_troubleshoot_mode[m.from_user.id] = False
    user_config_test_mode[m.from_user.id] = False
    await m.answer("🏠 **منوی اصلی** 😊", parse_mode="Markdown", reply_markup=get_main_menu_keyboard())

@router.message(F.text == "🚀 تست سرعت اینترنت")
async def btn_speed(m: types.Message, bot: Bot):
    await bot.send_chat_action(chat_id=m.chat.id, action="typing")
    result = await ConfigTester.speed_test_only()
    await m.answer(result, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())

@router.message(F.text == "🛍️ خرید اشتراک")
async def btn_shop(m: types.Message, bot: Bot):
    t = "🛍️ **برای خرید اشتراک، تست رایگان، تمدید و قیمت‌ها:** 👇\n\n🎁 @Alexvpn98bot"
    await m.answer(t, parse_mode="Markdown", reply_markup=get_shop_keyboard())

@router.message(F.text == "🆘 پشتیبانی")
async def btn_support(m: types.Message, bot: Bot):
    t = "🆘 **پشتیبانی انسانی:** 👇\n\n@Alexvpnsupport"
    await m.answer(t, parse_mode="Markdown", reply_markup=get_support_keyboard())

# INLINE CALLBACKS
@router.callback_query(F.data == "menu_main")
async def cb_mm(c: types.CallbackQuery):
    user_free_chat_mode[c.from_user.id] = False
    await c.message.answer("🏠 **منوی اصلی**", parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
    await c.answer()

for tutorial, name in [
    ("tutorial_happ", "🍏 **آموزش کامل HAPP (آیفون/آیپد)**\n\n""📥 **دانلود و نصب:**\n""• از اپ استور دانلود کن (لینک در 📥 دانلود)\n""• برنامه رو باز کن\n""• Allow Notifications رو بزن\n\n""🔗 **وارد کردن اشتراک:**\n""۱. لینک اشتراک رو کپی کن\n""۲. بالا سمت راست ➕ بزن\n""۳. Add From Clipboard رو انتخاب کن\n""۴. اسم بذار: Alex VPN\n""۵. Save رو بزن\n\n""🔄 **بروزرسانی:**\n""۱. تب Subscription (پایین)\n""۲. Update Subscription رو بزن\n""۳. صبر کن (۱۰-۳۰ ثانیه)\n""۴. پیغام Success = آماده\n\n""✅ **اتصال:**\n""۱. از لیست یه کانفیگ انتخاب کن\n""۲. Connect یا ▶️ بزن\n""۳. صبر کن وصل بشه\n""۴. یه سایت باز کن تست کن\n""۵. نشد ← کانفیگ بعدی\n\n""💡 **نکات حرفه‌ای:**\n""• قبل اتصال حتماً Update کن\n""• از Ping برای تست سرعت استفاده کن\n""• Auto Reconnect رو فعال کن\n""• هر ۴-۶ ساعت Update کن\n""• اگه کند بود، کانفیگ با پینگ کمتر انتخاب کن"),
    ("tutorial_foxray", "🍏 **آموزش کامل FoXray (آیفون/آیپد)**\n\n""📥 **دانلود و نصب:**\n""• از اپ استور دانلود کن\n""• برنامه رو باز کن و Allow Notifications\n\n""🔗 **وارد کردن اشتراک:**\n""۱. لینک رو کپی کن\n""۲. پایین صفحه Subscriptions رو بزن\n""۳. بالا سمت راست ➕\n""۴. لینک رو Paste کن\n""۵. اسم: Alex VPN\n""۶. Save\n\n""🔄 **بروزرسانی:**\n""۱. توی Subscriptions بمون\n""۲. روی اسم اشتراک بزن\n""۳. Update رو انتخاب کن\n""۴. صبر کن\n\n""✅ **اتصال:**\n""۱. برگرد به صفحه اصلی\n""۲. کانفیگ انتخاب کن\n""۳. Connect بزن\n""۴. تست کن با باز کردن سایت\n\n""💡 FoXray تنظیمات پیشرفته داره: Routing, DNS, Mux"),
    ("tutorial_streisand", "🍏 **Streisand (آیفون)**\n\n📥 اپ استور\n🔗 Subscriptions → ➕ → Paste → Save\n🔄 ↻ بروزرسانی\n✅ کانفیگ → Connect"),
    ("tutorial_v2rayng", "🤖 **آموزش کامل V2rayNG (اندروید)**\n\n""📥 **دانلود و نصب:**\n""• از منوی دانلود، APK رو بگیر\n""• فایل رو باز کن → Install\n""• Allow Unknown Sources رو بزن\n""• Open\n\n""🔗 **وارد کردن اشتراک:**\n""۱. لینک رو کپی کن\n""۲. بالا سمت راست ➕ (سه نقطه)\n""۳. گزینه Subscribe\n""۴. URL: Paste کن\n""۵. Remarks: Alex VPN\n""۶. ✅ OK\n\n""🔄 **بروزرسانی:**\n""۱. تب Subscription (بالا)\n""۲. آیکون ↻ رو بزن\n""۳. صبر کن (عدد کنارش = تعداد کانفیگ)\n""۴. هر ۴-۶ ساعت Update کن\n\n""✅ **اتصال:**\n""۱. از لیست یه کانفیگ انتخاب کن\n""۲. ▶️ Connect بزن\n""۳. آیکون VPN میاد بالا\n""۴. تست کن\n""۵. نشد ← کانفیگ بعدی\n\n""💡 **نکات طلایی:**\n""• Ping بگیر: Settings → Ping\n""• Auto Connect فعال کن\n""• Battery Optimization رو خاموش کن\n""• DNS: 8.8.8.8 (اگه مشکل داری)"),
    ("tutorial_nekobox", "🤖 **آموزش کامل Nekobox (اندروید)**\n\n""📥 **دانلود و نصب:**\n""• از منوی دانلود APK بگیر\n""• نصب کن\n\n""🔗 **وارد کردن اشتراک:**\n""۱. آیکون منو (سه خط) بالا چپ\n""۲. Subscriptions\n""۳. ➕ بالا\n""۴. Name: Alex VPN\n""۵. URL: Paste کن\n""۶. OK\n\n""🔄 **بروزرسانی:**\n""۱. روی اسم اشتراک بزن\n""۲. Update\n""۳. صبر کن\n\n""✅ **اتصال:**\n""۱. صفحه اصلی\n""۲. کانفیگ → ▶️\n""۳. تست کن\n\n""💡 Nekobox امکانات پیشرفته داره: Route, DNS, Mux, Auto Connect"),
    ("tutorial_hiddify", "🤖 **Hiddify (اندروید)**\n\n📥 دانلود APK → نصب\n🔗 Subscriptions → ➕ → Paste → Add\n🔄 Update All\n✅ کانفیگ → Connect"),
    ("tutorial_nekoray", "💻 **Nekoray (ویندوز)**\n\n📥 دانلود ZIP → Extract → اجرا\n🔗 Server → Add Subscription → Paste → OK\n🔄 Subscription → Update All\n✅ راست کلیک → Connect"),
    ("tutorial_hiddify_win", "💻 **Hiddify (ویندوز)**\n\n📥 دانلود exe → نصب\n🔗 Subscriptions → Add → Paste → Save\n🔄 Update All\n✅ کانفیگ → Connect"),
]:
    async def make_tutorial(c: types.CallbackQuery, text=name, tut=tutorial):
        await c.message.edit_text(text, parse_mode="Markdown", reply_markup=get_back_to_main_keyboard())
        await c.answer()
    router.callback_query(F.data == tutorial)(make_tutorial)

# ==================== MESSAGE HANDLER ====================

@router.message()
async def handle(m: types.Message, bot: Bot, groq_client: GroqClient):
    if m.chat.type != ChatType.PRIVATE or not m.text: return
    um = m.text.strip()
    if not um: return
    u = m.from_user

    # BROADCAST
    if admin_broadcast_mode.get(u.id) and is_admin(u.id):
        admin_broadcast_mode[u.id] = False
        users = admin.get_users_by_period("all")
        s, f = 0, 0
        st = await m.reply(f"📢 ارسال به {len(users)}...")
        for uu in users:
            try:
                await bot.send_message(uu["user_id"], f"📢 {um}", parse_mode="Markdown")
                s += 1
                await asyncio.sleep(0.3)
            except: f += 1
        await st.edit_text(f"✅ {s} | ❌ {f}")
        return

    # CONFIG TEST MODE
    if user_config_test_mode.get(u.id, False):
        user_config_test_mode[u.id] = False
        await bot.send_chat_action(chat_id=m.chat.id, action="typing")
        result = await ConfigTester.test_config(um)
        await m.reply(result, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
        return

    # TROUBLESHOOT MODE
    if user_troubleshoot_mode.get(u.id, False):
        admin.add_user(u.id, u.username or "", u.full_name)
        await bot.send_chat_action(chat_id=m.chat.id, action="typing")
        ai = await groq_client.get_response(u.id, f"کاربر در حال عیب‌یابی VPN هست. مشکلش: {um}\n\nلطفاً قدم به قدم راهنمایی کن و ازش بپرس چه دستگاه و برنامه‌ای داره. مثل یه پشتیبان واقعی رفتار کن.")
        await m.reply(ai + "\n\n🛍️ @Alexvpn98bot | 🆘 @Alexvpnsupport", parse_mode="Markdown", reply_markup=get_troubleshoot_keyboard())
        return

    admin.add_user(u.id, u.username or "", u.full_name)
    await bot.send_chat_action(chat_id=m.chat.id, action="typing")

    try:
        if check_for_shop_intent(um):
            t = "🛍️ **برای خرید، تست، تمدید →** @Alexvpn98bot"
            await reply_with_sound(m, bot, t, parse_mode="Markdown", reply_markup=get_shop_keyboard())
            return

        ai = await groq_client.get_response(u.id, um)
        contact = "\n\n━━━━━━━━━━━━━━━━\n🛍️ @Alexvpn98bot\n🆘 @Alexvpnsupport"
        final = ai + contact if "@Alexvpn98bot" not in ai else ai
        admin.log_chat(u.id, u.username or "", u.full_name, um, final)

        if check_for_human_support(ai):
            await reply_with_sound(m, bot, final)
            await m.answer("⚠️ پشتیبانی:", reply_markup=get_support_keyboard())
        else:
            is_free = user_free_chat_mode.get(u.id, False)
            kb = get_chat_keyboard() if is_free else get_main_menu_keyboard()
            await reply_with_sound(m, bot, final, reply_markup=kb)
    except Exception as e:
        logger.error(f"Error: {e}")
        await reply_with_sound(m, bot, "😅 مشکل!\n🛍️ @Alexvpn98bot | 🆘 @Alexvpnsupport", reply_markup=get_support_keyboard())

@router.error()
async def err(event: types.ErrorEvent):
    logger.critical(f"Error: {event.exception}")
