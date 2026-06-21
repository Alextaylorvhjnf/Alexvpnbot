#!/bin/bash
# ╔══════════════════════════════════════════════╗
# ║     🚀 AlexVPN Bot - Interactive Setup     ║
# ║     github.com/Alextaylorvhjnf/Alexvpnbot   ║
# ╚══════════════════════════════════════════════╝

set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; PURPLE='\033[0;35m'
NC='\033[0m'; BOLD='\033[1m'

REPO_URL="https://github.com/Alextaylorvhjnf/Alexvpnbot.git"
INSTALL_DIR="/root/Alexvpnbot"

clear
echo ""
echo -e "${PURPLE}${BOLD}╔══════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}${BOLD}║        🚀 A L E X   V P N   B O T          ║${NC}"
echo -e "${PURPLE}${BOLD}║        Interactive Setup v4.0              ║${NC}"
echo -e "${PURPLE}${BOLD}╚══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}  📡 Smart VPN Support Bot with AI${NC}"
echo -e "${CYAN}  🧠 Groq AI | ⚡ Real TCP Ping | 🚀 Speed Test${NC}"
echo ""

[ "$EUID" -ne 0 ] && echo -e "${RED}❌ Run as root!${NC}" && exit 1

# ──── MENU ────
show_menu() {
    echo ""
    echo -e "${BLUE}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}   📋 What would you like to do?${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "   ${GREEN}[1]${NC} 🚀 Fresh Install"
    echo -e "   ${YELLOW}[2]${NC} 🔄 Update Bot"
    echo -e "   ${CYAN}[3]${NC} 📊 View Status"
    echo -e "   ${CYAN}[4]${NC} 📋 View Logs"
    echo -e "   ${RED}[5]${NC} 🗑️  Uninstall Bot"
    echo -e "   ${CYAN}[6]${NC} 🔄 Restart Bot"
    echo -e "   ${CYAN}[7]${NC} 🛑 Stop Bot"
    echo -e "   ${CYAN}[8]${NC} ❌ Exit"
    echo ""
    read -p "   Select [1-8]: " CHOICE
    
    case $CHOICE in
        1) fresh_install ;;
        2) update_bot ;;
        3) show_status ;;
        4) show_logs ;;
        5) uninstall_bot ;;
        6) restart_bot ;;
        7) stop_bot ;;
        8) echo -e "${GREEN}👋 Goodbye!${NC}"; exit 0 ;;
        *) echo -e "${RED}Invalid choice${NC}"; show_menu ;;
    esac
}

# ──── FUNCTIONS ────
install_deps() {
    echo -e "\n${BLUE}━━━ 📦 Installing Dependencies ━━━${NC}\n"
    if ! command -v python3.12 &> /dev/null; then
        echo -e "${YELLOW}⏳ Installing Python 3.12...${NC}"
        apt update -qq 2>/dev/null
        apt install -y software-properties-common -qq 2>/dev/null
        add-apt-repository ppa:deadsnakes/ppa -y 2>/dev/null
        apt update -qq 2>/dev/null
        apt install -y python3.12 python3.12-venv python3.12-dev git curl ffmpeg -qq 2>/dev/null
        echo -e "${GREEN}✅ Python 3.12 installed${NC}"
    else
        echo -e "${GREEN}✅ Python 3.12 already installed${NC}"
    fi
    apt install -y git curl -qq 2>/dev/null
}

get_config() {
    echo -e "\n${BLUE}━━━ ⚙️  Configuration ━━━${NC}\n"
    echo -e "${CYAN}🔑 Telegram Bot Info:${NC}"
    read -p "   🤖 Bot Token: " BOT_TOKEN
    read -p "   👤 Admin ID: " ADMIN_ID
    read -p "   🧠 Groq API Key: " GROQ_API_KEY
    echo ""
    echo -e "${CYAN}📞 Support Info:${NC}"
    read -p "   🛍️ Shop Bot ID (e.g. Alexvpn98bot): " SHOP_ID
    read -p "   🆘 Support ID (e.g. Alexvpnsupport): " SUPPORT_ID
    SHOP_ID=$(echo "$SHOP_ID" | sed 's/^@//')
    SUPPORT_ID=$(echo "$SUPPORT_ID" | sed 's/^@//')
    echo -e "\n${GREEN}✅ Configuration saved!${NC}"
}

download_project() {
    echo -e "\n${BLUE}━━━ 📥 Downloading Project ━━━${NC}\n"
    if [ -d "$INSTALL_DIR" ]; then
        echo -e "${YELLOW}⚠️  Directory exists. Updating...${NC}"
        cd "$INSTALL_DIR"
        git pull origin main 2>/dev/null || true
    else
        git clone "$REPO_URL" "$INSTALL_DIR" 2>/dev/null || {
            echo -e "${YELLOW}⚠️  Trying with token...${NC}"
            git clone "https://Alextaylorvhjnf@github.com/Alextaylorvhjnf/Alexvpnbot.git" "$INSTALL_DIR" 2>/dev/null
        }
        cd "$INSTALL_DIR"
    fi
    echo -e "${GREEN}✅ Project downloaded${NC}"
}

setup_python() {
    echo -e "\n${BLUE}━━━ 📚 Python Setup ━━━${NC}\n"
    python3.12 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel -q 2>/dev/null
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt -q 2>/dev/null
    else
        pip install aiogram groq python-dotenv aiohttp -q 2>/dev/null
    fi
    echo -e "${GREEN}✅ Python packages installed${NC}"
}

create_env() {
    echo -e "\n${BLUE}━━━ 🔐 Saving Config ━━━${NC}\n"
    cat > .env << ENVEOF
BOT_TOKEN=$BOT_TOKEN
ADMIN_ID=$ADMIN_ID
GROQ_API_KEY=$GROQ_API_KEY
SHOP_BOT_ID=$SHOP_ID
SUPPORT_ID=$SUPPORT_ID
ENVEOF
    mkdir -p logs data
    echo -e "${GREEN}✅ .env created${NC}"
}

replace_ids() {
    echo -e "\n${BLUE}━━━ 🔧 Configuring Bot ━━━${NC}\n"
    for f in prompt.txt handlers.py keyboards.py; do
        [ -f "$f" ] && sed -i "s/@Alexvpn98bot/@$SHOP_ID/g; s/@Alexvpnsupport/@$SUPPORT_ID/g; s|https://t.me/Alexvpn98bot|https://t.me/$SHOP_ID|g; s|https://t.me/Alexvpnsupport|https://t.me/$SUPPORT_ID|g" "$f" && echo -e "${GREEN}✅ $f${NC}"
    done
}

setup_service() {
    echo -e "\n${BLUE}━━━ 🔄 Systemd Service ━━━${NC}\n"
    cat > /etc/systemd/system/alexvpnbot.service << SERV
[Unit]
Description=Alex VPN AI Assistant Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python bot.py
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
SERV
    systemctl daemon-reload
    systemctl enable alexvpnbot.service
    systemctl restart alexvpnbot.service
    sleep 3
    if systemctl is-active --quiet alexvpnbot.service; then
        echo -e "${GREEN}✅ Service running!${NC}"
    else
        echo -e "${RED}⚠️  Service failed${NC}"
    fi
}

fresh_install() {
    install_deps
    get_config
    download_project
    setup_python
    create_env
    replace_ids
    setup_service
    show_success
}

update_bot() {
    echo -e "\n${BLUE}━━━ 🔄 Updating Bot ━━━${NC}\n"
    cd "$INSTALL_DIR" 2>/dev/null || { echo -e "${RED}❌ Not installed${NC}"; show_menu; }
    git pull origin main 2>/dev/null
    source venv/bin/activate
    pip install -r requirements.txt -q 2>/dev/null
    systemctl restart alexvpnbot.service
    echo -e "${GREEN}✅ Bot updated and restarted!${NC}"
    show_menu
}

show_status() {
    echo -e "\n${BLUE}━━━ 📊 Status ━━━${NC}\n"
    systemctl status alexvpnbot.service --no-pager 2>/dev/null || echo -e "${RED}Service not found${NC}"
    show_menu
}

show_logs() {
    echo -e "\n${BLUE}━━━ 📋 Logs (Ctrl+C to exit) ━━━${NC}\n"
    journalctl -u alexvpnbot.service -f --no-pager 2>/dev/null || cat "$INSTALL_DIR/logs/bot.log" 2>/dev/null
    show_menu
}

uninstall_bot() {
    echo -e "\n${RED}━━━ 🗑️  Uninstall ━━━${NC}\n"
    read -p "   Are you sure? [y/N]: " CONFIRM
    if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
        systemctl stop alexvpnbot.service 2>/dev/null
        systemctl disable alexvpnbot.service 2>/dev/null
        rm -f /etc/systemd/system/alexvpnbot.service
        systemctl daemon-reload
        rm -rf "$INSTALL_DIR"
        echo -e "${GREEN}✅ Bot uninstalled!${NC}"
    else
        echo -e "${YELLOW}Cancelled${NC}"
    fi
    exit 0
}

restart_bot() {
    systemctl restart alexvpnbot.service 2>/dev/null
    echo -e "${GREEN}✅ Bot restarted!${NC}"
    show_menu
}

stop_bot() {
    systemctl stop alexvpnbot.service 2>/dev/null
    echo -e "${YELLOW}🛑 Bot stopped!${NC}"
    show_menu
}

show_success() {
    echo ""
    echo -e "${GREEN}${BOLD}╔══════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}${BOLD}║          🎉 Installation Complete!          ║${NC}"
    echo -e "${GREEN}${BOLD}╚══════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}📋 Configuration:${NC}"
    echo -e "   🤖 Token:    ${BOT_TOKEN:0:15}..."
    echo -e "   👤 Admin:    $ADMIN_ID"
    echo -e "   🛍️  Shop:     @$SHOP_ID"
    echo -e "   🆘 Support:  @$SUPPORT_ID"
    echo ""
    echo -e "${YELLOW}🔧 Commands:${NC}"
    echo -e "   status:   ${BOLD}sudo systemctl status alexvpnbot${NC}"
    echo -e "   restart:  ${BOLD}sudo systemctl restart alexvpnbot${NC}"
    echo -e "   logs:     ${BOLD}sudo journalctl -u alexvpnbot -f${NC}"
    echo ""
    echo -e "📁 Path: ${BOLD}$INSTALL_DIR${NC}"
    echo -e "🚀 Go to Telegram: ${BOLD}/start${NC}"
    echo ""
    echo -e "${CYAN}Run ${BOLD}bash $INSTALL_DIR/install.sh${NC} ${CYAN}for menu${NC}"
    echo ""
}

# ──── START ────
if [ -f "$INSTALL_DIR/.env" ]; then
    show_menu
else
    fresh_install
fi
