#!/bin/bash
# اسکریپت بکاپ کامل ربات AlexVPN
# اجرا: bash backup.sh

BACKUP_NAME="Alexvpnbot-backup-$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="/root/backups"
mkdir -p "$BACKUP_DIR"

echo "📦 در حال ساخت بکاپ کامل..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━"

# بکاپ کامل (بدون venv و cache)
cd ~
tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" \
    --exclude='Alexvpnbot/venv' \
    --exclude='Alexvpnbot/__pycache__' \
    --exclude='Alexvpnbot/*.pyc' \
    --exclude='Alexvpnbot/.git' \
    Alexvpnbot/

SIZE=$(du -h "$BACKUP_DIR/$BACKUP_NAME.tar.gz" | cut -f1)

echo ""
echo "✅ بکاپ با موفقیت ساخته شد!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 مسیر: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
echo "📦 حجم: $SIZE"
echo ""
echo "📋 محتویات بکاپ:"
echo "  • تمام فایل‌های Python (.py)"
echo "  • فایل‌های prompt.txt, requirements.txt"
echo "  • دیتابیس کاربران (data/users.json)"
echo "  • تاریخچه مکالمات (data/chats.json)"
echo "  • لاگ‌ها (logs/)"
echo "  • فایل .env (تنظیمات)"
echo ""
echo "📥 برای دانلود روی سیستم خودت:"
echo "  scp root@SERVER_IP:$BACKUP_DIR/$BACKUP_NAME.tar.gz ."
echo ""
echo "🔄 برای انتقال به سرور جدید:"
echo "  1. فایل رو به سرور جدید منتقل کن"
echo "  2. tar -xzf $BACKUP_NAME.tar.gz"
echo "  3. cd Alexvpnbot"
echo "  4. bash install.sh"
