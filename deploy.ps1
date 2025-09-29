# deploy.ps1 - PowerShell скрипт автоматического развертывания Telegram бота

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

Write-Log "🚀 Начинаем развертывание Telegram бота на сервер: $Server"

# Проверка подключения
Write-Log "📡 Проверка подключения к серверу..."
Write-Host "Введите пароль для подключения к серверу" -ForegroundColor Cyan
ssh -o ConnectTimeout=10 -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "echo 'Подключение успешно'" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Не удалось подключиться к серверу $Server"
    Write-Error "Проверьте:"
    Write-Error "1. Правильность пароля"
    Write-Error "2. Сервер доступен"
    Write-Error "3. Пользователь имеет права доступа"
    exit 1
}
Write-Success "Подключение к серверу установлено"

# Создание директории на сервере
Write-Log "📁 Создание директории на сервере..."
Write-Host "Введите пароль для создания директории" -ForegroundColor Cyan
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "mkdir -p $RemoteDir" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Не удалось создать директорию $RemoteDir"
    exit 1
}
Write-Success "Директория создана"

# Копирование файлов
Write-Log "📋 Копирование файлов проекта..."
Write-Host "Введите пароль для копирования файлов" -ForegroundColor Cyan
scp -o PreferredAuthentications=password -o PubkeyAuthentication=no -r "$LocalDir\*" "${Server}:${RemoteDir}/" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Не удалось скопировать файлы"
    exit 1
}
Write-Success "Файлы скопированы"

# Проверка наличия .env файла
Write-Log "🔍 Проверка конфигурации..."
Write-Host "Введите пароль для проверки .env файла" -ForegroundColor Cyan
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "test -f $RemoteDir/.env" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Warning ".env файл не найден на сервере"
    Write-Warning "Создайте .env файл с настройками:"
    Write-Warning "BOT_TOKEN=your_bot_token"
    Write-Warning "ADMIN_USER_IDS=your_admin_ids"
    Write-Warning "DATABASE_PATH=database.db"
}

# Установка зависимостей
Write-Log "📦 Установка зависимостей Python..."
Write-Host "Введите пароль для создания виртуального окружения" -ForegroundColor Cyan
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "cd $RemoteDir && python3 -m venv venv" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Не удалось создать виртуальное окружение"
    exit 1
}

Write-Host "Введите пароль для установки зависимостей" -ForegroundColor Cyan
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "cd $RemoteDir && source venv/bin/activate && pip install -r requirements.txt" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Не удалось установить зависимости"
    exit 1
}
Write-Success "Зависимости установлены"

# Настройка прав доступа
Write-Log "🔐 Настройка прав доступа..."
Write-Host "Введите пароль для настройки прав доступа" -ForegroundColor Cyan
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "cd $RemoteDir && chmod +x bot.py" | Out-Null
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "cd $RemoteDir && chmod 600 .env 2>/dev/null || true" | Out-Null
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "cd $RemoteDir && chmod 644 *.py" | Out-Null
Write-Success "Права доступа настроены"

# Создание systemd сервиса
Write-Log "⚙️ Настройка systemd сервиса..."
$serviceConfig = @"
[Unit]
Description=Telegram Bot Service
After=network.target

[Service]
Type=simple
User=`$(whoami)
Group=`$(whoami)
WorkingDirectory=$RemoteDir
Environment=PATH=$RemoteDir/venv/bin
ExecStart=$RemoteDir/venv/bin/python $RemoteDir/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"@

Write-Host "Введите пароль для создания systemd сервиса" -ForegroundColor Cyan
$serviceConfig | ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "sudo tee /etc/systemd/system/telegram-bot.service > /dev/null" | Out-Null

# Перезагрузка systemd
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "sudo systemctl daemon-reload" | Out-Null

# Включение автозапуска
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "sudo systemctl enable telegram-bot" | Out-Null

# Перезапуск сервиса
Write-Log "🔄 Перезапуск сервиса..."
Write-Host "Введите пароль для перезапуска сервиса" -ForegroundColor Cyan
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "sudo systemctl restart telegram-bot" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Не удалось перезапустить сервис"
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

# Показ логов
Write-Log "📋 Последние логи:"
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no $Server "sudo journalctl -u telegram-bot -n 10 --no-pager"

Write-Success "🎉 Развертывание завершено успешно!"
Write-Log "Для мониторинга используйте:"
Write-Log "  ssh -o PreferredAuthentications=password $Server 'sudo journalctl -u telegram-bot -f'"
Write-Log "  ssh -o PreferredAuthentications=password $Server 'sudo systemctl status telegram-bot'"
