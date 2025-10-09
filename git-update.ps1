# git-update.ps1 - PowerShell скрипт обновления Telegram бота через Git

param(
    [string]$Server = "telegram-bot-server",
    [string]$RemoteDir = "~/telegram-bot",
    [string]$RepoUrl = "https://github.com/goodfeeling1337-create/telegram-bot-applications.git"
)

# Функции для вывода сообщений
function Write-Log {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message" -ForegroundColor Blue
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

# Проверка аргументов
if ($args.Count -eq 1) {
    $Server = $args[0]
}

if ($args.Count -eq 2) {
    $Server = $args[0]
    $RepoUrl = $args[1]
}

Write-Log "🔄 Начинаем обновление Telegram бота через Git на сервере: $Server"
Write-Log "📦 Репозиторий: $RepoUrl"

# Проверка подключения
Write-Log "📡 Проверка подключения к серверу..."
ssh -o ConnectTimeout=10 -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "echo 'Подключение успешно'" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Не удалось подключиться к серверу $Server"
    exit 1
}
Write-Success "Подключение к серверу установлено"

# Проверка существования директории проекта
Write-Log "🔍 Проверка директории проекта..."
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "test -d $RemoteDir" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Директория проекта не найдена. Создаем новую..."
    ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "mkdir -p $RemoteDir" 2>$null
}

# Проверка Git репозитория
Write-Log "🔍 Проверка Git репозитория..."
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "cd $RemoteDir && git status" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Git репозиторий не инициализирован. Клонируем репозиторий..."
    ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "cd $(Split-Path $RemoteDir) && git clone $RepoUrl $(Split-Path $RemoteDir -Leaf)" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Не удалось клонировать репозиторий"
        exit 1
    }
    Write-Success "Репозиторий клонирован"
} else {
    # Проверка удаленного репозитория
    $CurrentRemote = ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "cd $RemoteDir && git remote get-url origin 2>/dev/null" 2>$null
    if ($CurrentRemote -ne $RepoUrl) {
        Write-Warning "URL удаленного репозитория отличается. Обновляем..."
        ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "cd $RemoteDir && git remote set-url origin $RepoUrl" 2>$null
    }
}

# Остановка сервиса
Write-Log "⏹️ Остановка сервиса..."
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "sudo systemctl stop telegram-bot" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Сервис telegram-bot не запущен или не существует"
}

# Создание резервной копии
Write-Log "💾 Создание резервной копии..."
$BackupName = "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "cd $RemoteDir && cp database.db database_${BackupName}.db 2>/dev/null || true" 2>$null
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "cd $RemoteDir && cp .env .env_${BackupName} 2>/dev/null || true" 2>$null
Write-Success "Резервная копия создана: ${BackupName}"

# Получение изменений из Git
Write-Log "📥 Получение изменений из Git..."
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "cd $RemoteDir && git fetch origin" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Не удалось получить изменения из Git"
    exit 1
}

# Показ изменений
Write-Log "📝 Просмотр изменений..."
$Changes = ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "cd $RemoteDir && git log HEAD..origin/main --oneline" 2>$null
if ([string]::IsNullOrEmpty($Changes)) {
    Write-Warning "Нет новых изменений для обновления"
    Write-Log "Текущая версия уже актуальна"
} else {
    Write-Log "Найдены следующие изменения:"
    Write-Host $Changes
}

# Обновление до последней версии
Write-Log "🔄 Обновление до последней версии..."
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "cd $RemoteDir && git pull origin main" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Не удалось обновить код через Git"
    exit 1
}
Write-Success "Код обновлен через Git"

# Показ текущего коммита
Write-Log "📋 Текущая версия:"
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "cd $RemoteDir && git log -1 --oneline"

# Обновление зависимостей
Write-Log "📦 Обновление зависимостей..."
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "cd $RemoteDir && source venv/bin/activate && pip install -r requirements.txt --upgrade" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Не удалось обновить зависимости"
    exit 1
}
Write-Success "Зависимости обновлены"

# Настройка прав доступа
Write-Log "🔐 Настройка прав доступа..."
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "cd $RemoteDir && chmod +x bot.py" | Out-Null
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "cd $RemoteDir && chmod 600 .env 2>/dev/null || true" | Out-Null
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "cd $RemoteDir && chmod 644 *.py" | Out-Null
Write-Success "Права доступа настроены"

# Перезагрузка systemd
Write-Log "⚙️ Перезагрузка systemd..."
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "sudo systemctl daemon-reload" | Out-Null

# Запуск сервиса
Write-Log "🚀 Запуск сервиса..."
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "sudo systemctl start telegram-bot" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Не удалось запустить сервис"
    exit 1
}

# Ожидание запуска
Start-Sleep -Seconds 3

# Проверка статуса
Write-Log "✅ Проверка статуса сервиса..."
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "sudo systemctl is-active --quiet telegram-bot" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Success "Сервис запущен успешно"
} else {
    Write-Error "Сервис не запущен"
    ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "sudo systemctl status telegram-bot --no-pager"
    exit 1
}

# Показ статуса
Write-Log "📊 Статус сервиса:"
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "sudo systemctl status telegram-bot --no-pager"

# Показ последних логов
Write-Log "📋 Последние логи:"
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "sudo journalctl -u telegram-bot -n 10 --no-pager"

Write-Success "🎉 Обновление через Git завершено успешно!"
Write-Log "Резервная копия: ${BackupName}"
Write-Log "Для мониторинга используйте:"
Write-Log "  ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server 'sudo journalctl -u telegram-bot -f'"
Write-Log "  ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server 'sudo systemctl status telegram-bot'"
Write-Log "  ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server 'cd $RemoteDir && git log --oneline -5'"
