```bash
# 🚀 Alex VPN AI Assistant Bot - نصب یک‌خطی

bash <(curl -s https://raw.githubusercontent.com/Alextaylorvhjnf/Alexvpnbot/main/install.sh)
```

---

## 📋 راهنمای کامل

### نصب روی سرور جدید (فقط یک خط):
```bash
bash <(curl -s https://raw.githubusercontent.com/Alextaylorvhjnf/Alexvpnbot/main/install.sh)
```

### یا دستی:
```bash
git clone https://github.com/Alextaylorvhjnf/Alexvpnbot.git
cd Alexvpnbot
bash install.sh
```

### بعد از اجرا، ازت میپرسه:
- 🤖 **Bot Token** (از @BotFather بگیر)
- 👤 **Admin ID** (ایدی عددی تلگرام خودت)
- 🧠 **Groq API Key** (از console.groq.com بگیر)

### بعد خودکار:
- ✅ Python 3.12 نصب میکنه
- ✅ محیط مجازی میسازه
- ✅ کتابخانه‌ها رو نصب میکنه
- ✅ فایل .env رو میسازه
- ✅ ربات رو تست میکنه
- ✅ سرویس systemd راه‌اندازی میکنه
- ✅ ربات ۲۴/۷ آنلاین میشه

---

### 🔧 دستورات مدیریتی:
```bash
sudo systemctl status alexvpnbot   # وضعیت
sudo systemctl restart alexvpnbot  # ریستارت
sudo systemctl stop alexvpnbot     # توقف
sudo journalctl -u alexvpnbot -f   # لاگ زنده
```

---

### 📦 بکاپ:
```bash
cd ~/Alexvpnbot
bash backup.sh        # بکاپ کد + دیتابیس
bash full_backup.sh   # بکاپ کامل با venv
```

---

### 🛍️ پشتیبانی:
- خرید: @Alexvpn98bot
- پشتیبانی: @Alexvpnsupport
