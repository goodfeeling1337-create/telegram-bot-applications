#!/bin/bash
# deploy.sh - Скрипт автоматического развертывания Telegram бота

# Конфигурация
SERVER="telegram-bot-server"
REMOTE_DIR="~/telegram-bot"
LOCAL_DIR="."

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Проверка аргументов
if [ $# -eq 1 ]; then
    SERVER="$1"
fi

log "🚀 Начинаем развертывание Telegram бота на сервер: $SERVER"

# Проверка подключения
log "📡 Проверка подключения к серверу..."
echo "Введите пароль для подключения к серверу"
if ! ssh -o ConnectTimeout=10 -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "echo 'Подключение успешно'" >/dev/null 2>&1; then
    error "Не удалось подключиться к серверу $SERVER"
    error "Проверьте:"
    error "1. Правильность пароля"
    error "2. Сервер доступен"
    error "3. Пользователь имеет права доступа"
    exit 1
fi
success "Подключение к серверу установлено"

# Создание директории на сервере
log "📁 Создание директории на сервере..."
if ! ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "mkdir -p $REMOTE_DIR"; then
    error "Не удалось создать директорию $REMOTE_DIR"
    exit 1
fi
success "Директория создана"

# Копирование файлов
log "📋 Копирование файлов проекта..."
if ! scp -o PreferredAuthentications=password -o PubkeyAuthentication=no -r $LOCAL_DIR/* $SERVER:$REMOTE_DIR/; then
    error "Не удалось скопировать файлы"
    exit 1
fi
success "Файлы скопированы"

# Проверка наличия .env файла
log "🔍 Проверка конфигурации..."
if ! ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "test -f $REMOTE_DIR/.env"; then
    warning ".env файл не найден на сервере"
    warning "Создайте .env файл с настройками:"
    warning "BOT_TOKEN=your_bot_token"
    warning "ADMIN_USER_IDS=your_admin_ids"
    warning "DATABASE_PATH=database.db"
fi

# Установка зависимостей
log "📦 Установка зависимостей Python..."
if ! ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "cd $REMOTE_DIR && python3 -m venv venv"; then
    error "Не удалось создать виртуальное окружение"
    exit 1
fi

if ! ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "cd $REMOTE_DIR && source venv/bin/activate && pip install -r requirements.txt"; then
    error "Не удалось установить зависимости"
    exit 1
fi
success "Зависимости установлены"

# Настройка прав доступа
log "🔐 Настройка прав доступа..."
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "cd $REMOTE_DIR && chmod +x bot.py"
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "cd $REMOTE_DIR && chmod 600 .env 2>/dev/null || true"
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "cd $REMOTE_DIR && chmod 644 *.py"
success "Права доступа настроены"

# Создание systemd сервиса
log "⚙️ Настройка systemd сервиса..."
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "sudo tee /etc/systemd/system/telegram-bot.service > /dev/null << 'EOF'
[Unit]
Description=Telegram Bot Service
After=network.target

[Service]
Type=simple
User=\$(whoami)
Group=\$(whoami)
WorkingDirectory=$REMOTE_DIR
Environment=PATH=$REMOTE_DIR/venv/bin
ExecStart=$REMOTE_DIR/venv/bin/python $REMOTE_DIR/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF"

# Перезагрузка systemd
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "sudo systemctl daemon-reload"

# Включение автозапуска
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "sudo systemctl enable telegram-bot"

# Перезапуск сервиса
log "🔄 Перезапуск сервиса..."
if ! ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "sudo systemctl restart telegram-bot"; then
    error "Не удалось перезапустить сервис"
    exit 1
fi

# Ожидание запуска
sleep 3

# Проверка статуса
log "✅ Проверка статуса сервиса..."
if ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "sudo systemctl is-active --quiet telegram-bot"; then
    success "Сервис запущен успешно"
else
    error "Сервис не запущен"
    ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "sudo systemctl status telegram-bot --no-pager"
    exit 1
fi

# Показ статуса
log "📊 Статус сервиса:"
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "sudo systemctl status telegram-bot --no-pager"

# Показ логов
log "📋 Последние логи:"
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "sudo journalctl -u telegram-bot -n 10 --no-pager"

success "🎉 Развертывание завершено успешно!"
log "Для мониторинга используйте:"
log "  ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER 'sudo journalctl -u telegram-bot -f'"
log "  ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER 'sudo systemctl status telegram-bot'"
