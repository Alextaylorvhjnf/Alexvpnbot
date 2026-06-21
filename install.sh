#!/bin/bash
# ╔══════════════════════════════════════════════╗
# ║     🚀 AlexVPN Bot - نصب تعاملی v3.0       ║
# ║     github.com/Alextaylorvhjnf/Alexvpnbot   ║
# ╚══════════════════════════════════════════════╝

set -e

# رنگ‌ها
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

REPO_URL="https://github.com/Alextaylorvhjnf/Alexvpnbot.git"
REPO_RAW="https://raw.githubusercontent.com/Alextaylorvhjnf/Alexvpnbot/main"
INSTALL_DIR="/root/Alexvpnbot"

clear
echo ""
echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}║     🚀 AlexVPN Bot - Installer v3.0        ║${NC}"
echo -e "${CYAN}${BOLD}║     github.com/Alextaylorvhjnf/Alexvpnbot   ║${NC}"
echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════════╝${NC}"
echo ""

# ──── ROOT CHECK ────
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ این اسکریپت باید با دسترسی root اجرا بشه!${NC}"
    echo -e "   sudo bash install.sh"
    exit 1
fi

# ──── STEP 1: System Requirements ────
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}📦 مرحله ۱: نصب پیش‌نیازهای سیستم${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if ! command -v python3.12 &> /dev/null; then
    echo -e "${YELLOW}⏳ در حال نصب Python 3.12...${NC}"
    apt update -qq 2>/dev/null
    apt install -y software-properties-common -qq 2>/dev/null
    add-apt-repository ppa:deadsnakes/ppa -y 2>/dev/null
    apt update -qq 2>/dev/null
    apt install -y python3.12 python3.12-venv python3.12-dev git curl ffmpeg -qq 2>/dev/null
    echo -e "${GREEN}✅ Python 3.12 نصب شد${NC}"
else
    echo -e "${GREEN}✅ Python 3.12 قبلاً نصب شده${NC}"
fi

if ! command -v git &> /dev/null; then
    apt install -y git -qq 2>/dev/null
fi

echo ""

# ──── STEP 2: Get Configuration ────
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}⚙️  مرحله ۲: پیکربندی ربات${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${CYAN}🔑 اطلاعات ربات تلگرام:${NC}"
echo ""
read -p "   🤖 Bot Token (از @BotFather): " BOT_TOKEN
read -p "   👤 Admin ID (ایدی عددی خودت): " ADMIN_ID
read -p "   🧠 Groq API Key (از console.groq.com): " GROQ_API_KEY
echo ""
echo -e "${CYAN}📞 اطلاعات پشتیبانی و فروش:${NC}"
echo ""
read -p "   🛍️ آیدی ربات فروش (مثال: Alexvpn98bot): " SHOP_ID
read -p "   🆘 آیدی پشتیبانی (مثال: Alexvpnsupport): " SUPPORT_ID

# Clean @ from IDs
SHOP_ID=$(echo "$SHOP_ID" | sed 's/^@//')
SUPPORT_ID=$(echo "$SUPPORT_ID" | sed 's/^@//')

echo ""
echo -e "${GREEN}✅ اطلاعات دریافت شد!${NC}"
echo ""

# ──── STEP 3: Download Project ────
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}📥 مرحله ۳: دانلود پروژه از گیت‌هاب${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}⚠️  پوشه Alexvpnbot وجود داره. در حال بروزرسانی...${NC}"
    cd "$INSTALL_DIR"
    git pull origin main 2>/dev/null || true
else
    echo -e "${YELLOW}⏳ در حال دانلود پروژه...${NC}"
    git clone "$REPO_URL" "$INSTALL_DIR" 2>/dev/null || {
        echo -e "${RED}❌ خطا در دانلود. با Token تلاش میکنم...${NC}"
        git clone "https://Alextaylorvhjnf@github.com/Alextaylorvhjnf/Alexvpnbot.git" "$INSTALL_DIR" 2>/dev/null
    }
    cd "$INSTALL_DIR"
fi

echo -e "${GREEN}✅ پروژه دانلود شد!${NC}"
echo ""

# ──── STEP 4: Python Setup ────
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}📚 مرحله ۴: نصب کتابخانه‌های Python${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel -q 2>/dev/null

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -q 2>/dev/null
    echo -e "${GREEN}✅ کتابخانه‌ها نصب شدن!${NC}"
else
    echo -e "${YELLOW}⚠️  requirements.txt پیدا نشد. نصب دستی...${NC}"
    pip install aiogram groq python-dotenv aiohttp -q 2>/dev/null
fi

echo ""

# ──── STEP 5: Create .env ────
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}🔐 مرحله ۵: ذخیره تنظیمات${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cat > .env << ENVEOF
BOT_TOKEN=$BOT_TOKEN
ADMIN_ID=$ADMIN_ID
GROQ_API_KEY=$GROQ_API_KEY
SHOP_BOT_ID=$SHOP_ID
SUPPORT_ID=$SUPPORT_ID
ENVEOF

mkdir -p logs data
echo -e "${GREEN}✅ فایل .env ساخته شد${NC}"
echo ""

# ──── STEP 6: Replace IDs in project files ────
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}🔧 مرحله ۶: تنظیم آیدی‌ها در ربات${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ -f "prompt.txt" ]; then
    sed -i "s/@Alexvpn98bot/@$SHOP_ID/g" prompt.txt
    sed -i "s/@Alexvpnsupport/@$SUPPORT_ID/g" prompt.txt
    echo -e "${GREEN}✅ prompt.txt${NC}"
fi

if [ -f "handlers.py" ]; then
    sed -i "s/@Alexvpn98bot/@$SHOP_ID/g" handlers.py
    sed -i "s/@Alexvpnsupport/@$SUPPORT_ID/g" handlers.py
    sed -i "s|https://t.me/Alexvpn98bot|https://t.me/$SHOP_ID|g" handlers.py
    sed -i "s|https://t.me/Alexvpnsupport|https://t.me/$SUPPORT_ID|g" handlers.py
    echo -e "${GREEN}✅ handlers.py${NC}"
fi

if [ -f "keyboards.py" ]; then
    sed -i "s|https://t.me/Alexvpn98bot|https://t.me/$SHOP_ID|g" keyboards.py
    sed -i "s|https://t.me/Alexvpnsupport|https://t.me/$SUPPORT_ID|g" keyboards.py
    echo -e "${GREEN}✅ keyboards.py${NC}"
fi

echo ""

# ──── STEP 7: Test Run ────
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}🧪 مرحله ۷: تست اجرای ربات${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

timeout 5 python bot.py 2>/dev/null &
PID=$!
sleep 5
kill $PID 2>/dev/null

if [ -f "logs/bot.log" ]; then
    echo -e "${GREEN}✅ ربات تست شد (لاگ موجوده)${NC}"
else
    echo -e "${YELLOW}⚠️  لاگ ساخته نشد${NC}"
fi

deactivate
echo ""

# ──── STEP 8: Systemd Service ────
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}🔄 مرحله ۸: راه‌اندازی سرویس خودکار${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

CURRENT_DIR=$(pwd)

cat > /etc/systemd/system/alexvpnbot.service << SERVICE
[Unit]
Description=Alex VPN AI Assistant Bot
After=network.target

[Service]
Type=simple
User=root
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
systemctl restart alexvpnbot.service
sleep 3

if systemctl is-active --quiet alexvpnbot.service; then
    echo -e "${GREEN}✅ سرویس با موفقیت راه‌اندازی شد!${NC}"
else
    echo -e "${RED}⚠️  سرویس راه‌اندازی نشد.${NC}"
fi

echo ""
echo -e "${GREEN}${BOLD}╔══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}${BOLD}║        🎉 نصب با موفقیت انجام شد!           ║${NC}"
echo -e "${GREEN}${BOLD}╚══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}📋 اطلاعات ربات:${NC}"
echo -e "   🤖 Token:    ${BOT_TOKEN:0:15}..."
echo -e "   👤 Admin:    $ADMIN_ID"
echo -e "   🧠 Groq:     ${GROQ_API_KEY:0:15}..."
echo -e "   🛍️  فروش:     @$SHOP_ID"
echo -e "   🆘 پشتیبانی: @$SUPPORT_ID"
echo ""
echo -e "${YELLOW}🔧 دستورات مدیریتی:${NC}"
echo -e "   وضعیت:   ${BOLD}sudo systemctl status alexvpnbot${NC}"
echo -e "   ریستارت: ${BOLD}sudo systemctl restart alexvpnbot${NC}"
echo -e "   توقف:    ${BOLD}sudo systemctl stop alexvpnbot${NC}"
echo -e "   لاگ:     ${BOLD}sudo journalctl -u alexvpnbot -f${NC}"
echo ""
echo -e "📁 مسیر: ${BOLD}$CURRENT_DIR${NC}"
echo -e "🚀 برو تو تلگرام: ${BOLD}/start${NC}"
echo ""
