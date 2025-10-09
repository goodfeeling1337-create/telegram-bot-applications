#!/bin/bash
# update.sh - Скрипт быстрого обновления Telegram бота на сервере

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

# Функции для вывода сообщений
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

log "🔄 Начинаем обновление Telegram бота на сервере: $SERVER"

# Проверка подключения
log "📡 Проверка подключения к серверу..."
if ! ssh -o ConnectTimeout=10 -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "echo 'Подключение успешно'" >/dev/null 2>&1; then
    error "Не удалось подключиться к серверу $SERVER"
    exit 1
fi
success "Подключение к серверу установлено"

# Остановка сервиса
log "⏹️ Остановка сервиса..."
if ! ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "sudo systemctl stop telegram-bot"; then
    error "Не удалось остановить сервис"
    exit 1
fi
success "Сервис остановлен"

# Создание резервной копии
log "💾 Создание резервной копии..."
BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S)"
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "cd $REMOTE_DIR && cp database.db database_${BACKUP_NAME}.db 2>/dev/null || true"
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "cd $REMOTE_DIR && cp .env .env_${BACKUP_NAME} 2>/dev/null || true"
success "Резервная копия создана: ${BACKUP_NAME}"

# Копирование обновленных файлов
log "📋 Копирование обновленных файлов..."
if ! scp -o PreferredAuthentications=password -o PubkeyAuthentication=no -r $LOCAL_DIR/* $SERVER:$REMOTE_DIR/; then
    error "Не удалось скопировать файлы"
    exit 1
fi
success "Файлы скопированы"

# Обновление зависимостей
log "📦 Обновление зависимостей..."
if ! ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "cd $REMOTE_DIR && source venv/bin/activate && pip install -r requirements.txt --upgrade"; then
    error "Не удалось обновить зависимости"
    exit 1
fi
success "Зависимости обновлены"

# Настройка прав доступа
log "🔐 Настройка прав доступа..."
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "cd $REMOTE_DIR && chmod +x bot.py"
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "cd $REMOTE_DIR && chmod 600 .env 2>/dev/null || true"
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "cd $REMOTE_DIR && chmod 644 *.py"
success "Права доступа настроены"

# Перезагрузка systemd
log "⚙️ Перезагрузка systemd..."
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "sudo systemctl daemon-reload"

# Запуск сервиса
log "🚀 Запуск сервиса..."
if ! ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "sudo systemctl start telegram-bot"; then
    error "Не удалось запустить сервис"
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

# Показ последних логов
log "📋 Последние логи:"
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "sudo journalctl -u telegram-bot -n 10 --no-pager"

success "🎉 Обновление завершено успешно!"
log "Резервная копия: ${BACKUP_NAME}"
log "Для мониторинга используйте:"
log "  ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER 'sudo journalctl -u telegram-bot -f'"
log "  ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER 'sudo systemctl status telegram-bot'"
