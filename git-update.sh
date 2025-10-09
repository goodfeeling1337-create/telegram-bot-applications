#!/bin/bash
# git-update.sh - Скрипт обновления Telegram бота через Git

# Конфигурация
SERVER="telegram-bot-server"
REMOTE_DIR="~/telegram-bot"
REPO_URL="https://github.com/goodfeeling1337-create/telegram-bot-applications.git"

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

if [ $# -eq 2 ]; then
    SERVER="$1"
    REPO_URL="$2"
fi

log "🔄 Начинаем обновление Telegram бота через Git на сервере: $SERVER"
log "📦 Репозиторий: $REPO_URL"

# Проверка подключения
log "📡 Проверка подключения к серверу..."
if ! ssh -o ConnectTimeout=10 -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "echo 'Подключение успешно'" >/dev/null 2>&1; then
    error "Не удалось подключиться к серверу $SERVER"
    exit 1
fi
success "Подключение к серверу установлено"

# Проверка существования директории проекта
log "🔍 Проверка директории проекта..."
if ! ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "test -d $REMOTE_DIR"; then
    warning "Директория проекта не найдена. Создаем новую..."
    ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "mkdir -p $REMOTE_DIR"
fi

# Проверка Git репозитория
log "🔍 Проверка Git репозитория..."
if ! ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "cd $REMOTE_DIR && git status" >/dev/null 2>&1; then
    warning "Git репозиторий не инициализирован. Клонируем репозиторий..."
    ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "cd $(dirname $REMOTE_DIR) && git clone $REPO_URL $(basename $REMOTE_DIR)"
    if [ $? -ne 0 ]; then
        error "Не удалось клонировать репозиторий"
        exit 1
    fi
    success "Репозиторий клонирован"
else
    # Проверка удаленного репозитория
    CURRENT_REMOTE=$(ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "cd $REMOTE_DIR && git remote get-url origin 2>/dev/null")
    if [ "$CURRENT_REMOTE" != "$REPO_URL" ]; then
        warning "URL удаленного репозитория отличается. Обновляем..."
        ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "cd $REMOTE_DIR && git remote set-url origin $REPO_URL"
    fi
fi

# Остановка сервиса
log "⏹️ Остановка сервиса..."
if ! ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "sudo systemctl stop telegram-bot"; then
    warning "Сервис telegram-bot не запущен или не существует"
fi

# Создание резервной копии
log "💾 Создание резервной копии..."
BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S)"
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "cd $REMOTE_DIR && cp database.db database_${BACKUP_NAME}.db 2>/dev/null || true"
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "cd $REMOTE_DIR && cp .env .env_${BACKUP_NAME} 2>/dev/null || true"
success "Резервная копия создана: ${BACKUP_NAME}"

# Получение изменений из Git
log "📥 Получение изменений из Git..."
if ! ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "cd $REMOTE_DIR && git fetch origin"; then
    error "Не удалось получить изменения из Git"
    exit 1
fi

# Показ изменений
log "📝 Просмотр изменений..."
CHANGES=$(ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "cd $REMOTE_DIR && git log HEAD..origin/main --oneline")
if [ -z "$CHANGES" ]; then
    warning "Нет новых изменений для обновления"
    log "Текущая версия уже актуальна"
else
    log "Найдены следующие изменения:"
    echo "$CHANGES"
fi

# Обновление до последней версии
log "🔄 Обновление до последней версии..."
if ! ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "cd $REMOTE_DIR && git pull origin main"; then
    error "Не удалось обновить код через Git"
    exit 1
fi
success "Код обновлен через Git"

# Показ текущего коммита
log "📋 Текущая версия:"
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER "cd $REMOTE_DIR && git log -1 --oneline"

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

success "🎉 Обновление через Git завершено успешно!"
log "Резервная копия: ${BACKUP_NAME}"
log "Для мониторинга используйте:"
log "  ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER 'sudo journalctl -u telegram-bot -f'"
log "  ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER 'sudo systemctl status telegram-bot'"
log "  ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $SERVER 'cd $REMOTE_DIR && git log --oneline -5'"
