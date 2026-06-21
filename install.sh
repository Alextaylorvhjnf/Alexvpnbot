#!/bin/bash
# 🚀 اسکریپت نصب تعاملی AlexVPN Bot
# اجرا: bash install.sh

clear
echo ""
echo "╔══════════════════════════════════════╗"
echo "║   🚀 AlexVPN Bot - نصب تعاملی      ║"
echo "║   Interactive Setup v1.0           ║"
echo "╚══════════════════════════════════════╝"
echo ""

# چک کردن root
if [ "$EUID" -ne 0 ]; then
    echo "❌ این اسکریپت باید با دسترسی root اجرا بشه!"
    echo "   sudo bash install.sh"
    exit 1
fi

# ─── مرحله ۱: نصب پیش‌نیازها ───
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 مرحله ۱: نصب پیش‌نیازها"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# نصب Python 3.12
if ! command -v python3.12 &> /dev/null; then
    echo "⏳ در حال نصب Python 3.12..."
    apt update -qq
    apt install -y software-properties-common -qq
    add-apt-repository ppa:deadsnakes/ppa -y
    apt update -qq
    apt install -y python3.12 python3.12-venv python3.12-dev git curl ffmpeg -qq
else
    echo "✅ Python 3.12 قبلاً نصب شده"
fi

echo ""
echo "✅ پیش‌نیازها نصب شدن!"
echo ""

# ─── مرحله ۲: تنظیمات ربات ───
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚙️  مرحله ۲: تنظیمات ربات"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# توکن ربات
echo "🔑 لطفاً اطلاعات ربات تلگرام رو وارد کن:"
echo ""
read -p "   🤖 Bot Token (از BotFather): " BOT_TOKEN
read -p "   👤 Admin ID (ایدی عددی خودت): " ADMIN_ID
read -p "   🧠 Groq API Key (از GroqCloud): " GROQ_API_KEY

echo ""
echo "✅ اطلاعات دریافت شد!"
echo ""

# ─── مرحله ۳: نصب محیط مجازی و کتابخانه‌ها ───
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📚 مرحله ۳: نصب کتابخانه‌های Python"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel -q
pip install -r requirements.txt -q

echo ""
echo "✅ کتابخانه‌ها نصب شدن!"
echo ""

# ─── مرحله ۴: ساخت فایل .env ───
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔐 مرحله ۴: ذخیره تنظیمات"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > .env << ENVEOF
BOT_TOKEN=$BOT_TOKEN
ADMIN_ID=$ADMIN_ID
GROQ_API_KEY=$GROQ_API_KEY
ENVEOF

# ساخت پوشه‌های مورد نیاز
mkdir -p logs data

echo "✅ فایل .env ساخته شد!"
echo ""

# ─── مرحله ۵: تست اجرا ───
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 مرحله ۵: تست اجرای ربات"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "⏳ در حال تست ربات (۵ ثانیه)..."
timeout 5 python bot.py 2>/dev/null &
PID=$!
sleep 5
kill $PID 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ ربات با موفقیت تست شد!"
else
    echo "⚠️ ربات تست نشد. لاگ رو چک کن: logs/bot.log"
fi

deactivate

echo ""

# ─── مرحله ۶: سرویس systemd ───
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔄 مرحله ۶: نصب سرویس خودکار"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

CURRENT_DIR=$(pwd)
CURRENT_USER=$(whoami)

cat > /etc/systemd/system/alexvpnbot.service << SERVICE
[Unit]
Description=Alex VPN AI Assistant Telegram Bot
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
ExecStart=$CURRENT_DIR/venv/bin/python bot.py
Restart=on-failure
RestartSec=10s
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable alexvpnbot.service
systemctl start alexvpnbot.service
sleep 2

if systemctl is-active --quiet alexvpnbot.service; then
    echo "✅ سرویس با موفقیت راه‌اندازی شد!"
else
    echo "⚠️ سرویس راه‌اندازی نشد. بررسی: systemctl status alexvpnbot"
fi

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   🎉 نصب با موفقیت انجام شد!       ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "📋 اطلاعات ربات:"
echo "   🤖 Token: ${BOT_TOKEN:0:15}..."
echo "   👤 Admin: $ADMIN_ID"
echo "   🧠 Groq: ${GROQ_API_KEY:0:15}..."
echo ""
echo "🔧 دستورات مدیریتی:"
echo "   • وضعیت:  sudo systemctl status alexvpnbot"
echo "   • ریستارت: sudo systemctl restart alexvpnbot"
echo "   • توقف:   sudo systemctl stop alexvpnbot"
echo "   • لاگ:    sudo journalctl -u alexvpnbot -f"
echo ""
echo "📁 مسیر پروژه: $CURRENT_DIR"
echo "📋 لاگ‌ها: $CURRENT_DIR/logs/bot.log"
echo ""
echo "🚀 ربات شما آماده‌ست! برو تو تلگرام /start بزن."
echo ""
