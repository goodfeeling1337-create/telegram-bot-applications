# update.ps1 - PowerShell скрипт быстрого обновления Telegram бота на сервере

param(
    [string]$Server = "telegram-bot-server",
    [string]$RemoteDir = "~/telegram-bot",
    [string]$LocalDir = "."
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

Write-Log "🔄 Начинаем обновление Telegram бота на сервере: $Server"

# Проверка подключения
Write-Log "📡 Проверка подключения к серверу..."
ssh -o ConnectTimeout=10 -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "echo 'Подключение успешно'" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Не удалось подключиться к серверу $Server"
    exit 1
}
Write-Success "Подключение к серверу установлено"

# Остановка сервиса
Write-Log "⏹️ Остановка сервиса..."
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "sudo systemctl stop telegram-bot" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Не удалось остановить сервис"
    exit 1
}
Write-Success "Сервис остановлен"

# Создание резервной копии
Write-Log "💾 Создание резервной копии..."
$BackupName = "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "cd $RemoteDir && cp database.db database_${BackupName}.db 2>/dev/null || true" 2>$null
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "cd $RemoteDir && cp .env .env_${BackupName} 2>/dev/null || true" 2>$null
Write-Success "Резервная копия создана: ${BackupName}"

# Копирование обновленных файлов
Write-Log "📋 Копирование обновленных файлов..."
scp -o PreferredAuthentications=password -o PubkeyAuthentication=no -r "${LocalDir}\*" "${Server}:${RemoteDir}/" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Не удалось скопировать файлы"
    exit 1
}
Write-Success "Файлы скопированы"

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

Write-Success "🎉 Обновление завершено успешно!"
Write-Log "Резервная копия: ${BackupName}"
Write-Log "Для мониторинга используйте:"
Write-Log "  ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server 'sudo journalctl -u telegram-bot -f'"
Write-Log "  ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server 'sudo systemctl status telegram-bot'"
