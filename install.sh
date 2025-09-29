#!/bin/bash
# install.sh - Быстрая установка Telegram бота

echo "🚀 Установка Telegram бота..."

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установка..."
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install python3 python3-pip python3-venv -y
    elif command -v yum &> /dev/null; then
        sudo yum install python3 python3-pip -y
    else
        echo "❌ Не удалось установить Python3 автоматически"
        exit 1
    fi
fi

# Создание виртуального окружения
echo "📦 Создание виртуального окружения..."
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
echo "📋 Установка зависимостей..."
pip install -r requirements.txt

# Создание .env файла если не существует
if [ ! -f .env ]; then
    echo "⚙️ Создание .env файла..."
    cat > .env << 'EOF'
BOT_TOKEN=your_bot_token_here
ADMIN_USER_IDS=your_admin_id1,your_admin_id2
DATABASE_PATH=database.db
EOF
    echo "📝 Отредактируйте .env файл с вашими настройками"
fi

# Настройка прав доступа
echo "🔐 Настройка прав доступа..."
chmod +x bot.py

echo "✅ Установка завершена!"
echo ""
echo "📝 Следующие шаги:"
echo "1. Отредактируйте .env файл: nano .env"
echo "2. Запустите бота: python bot.py"
echo "3. Или используйте systemd сервис (см. INSTALL.md)"
