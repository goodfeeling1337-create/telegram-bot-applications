# install.ps1 - Быстрая установка Telegram бота для Windows

Write-Host "🚀 Установка Telegram бота..." -ForegroundColor Green

# Проверка Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python не найден. Установите Python с python.org" -ForegroundColor Red
    Write-Host "Скачайте Python: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Создание виртуального окружения
Write-Host "📦 Создание виртуального окружения..." -ForegroundColor Yellow
python -m venv venv

# Активация виртуального окружения
Write-Host "🔧 Активация виртуального окружения..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Установка зависимостей
Write-Host "📋 Установка зависимостей..." -ForegroundColor Yellow
pip install -r requirements.txt

# Создание .env файла если не существует
if (-not (Test-Path .env)) {
    Write-Host "⚙️ Создание .env файла..." -ForegroundColor Yellow
    @"
BOT_TOKEN=your_bot_token_here
ADMIN_USER_IDS=your_admin_id1,your_admin_id2
DATABASE_PATH=database.db
"@ | Out-File -FilePath .env -Encoding UTF8
    Write-Host "📝 Отредактируйте .env файл с вашими настройками" -ForegroundColor Cyan
}

Write-Host "✅ Установка завершена!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Следующие шаги:" -ForegroundColor Cyan
Write-Host "1. Отредактируйте .env файл: notepad .env" -ForegroundColor White
Write-Host "2. Запустите бота: python bot.py" -ForegroundColor White
Write-Host "3. Или используйте systemd сервис (см. INSTALL.md)" -ForegroundColor White
