# 🚀 Руководство по развертыванию Telegram бота

## 📋 Предварительные требования

### Системные требования
- Python 3.8 или выше
- Linux/Windows/macOS сервер
- Минимум 512MB RAM
- 1GB свободного места на диске

### Необходимые права
- Доступ к серверу по SSH
- Права на установку пакетов
- Возможность создания systemd сервиса (для Linux)

## 🔧 Установка на сервер

### 1. Подготовка сервера

```bash
# Обновление системы (Ubuntu/Debian)
sudo apt update && sudo apt upgrade -y

# Установка Python и pip
sudo apt install python3 python3-pip python3-venv -y

# Создание пользователя для бота
sudo useradd -m -s /bin/bash telegram-bot
sudo su - telegram-bot
```

### 2. Клонирование проекта

```bash
# Создание директории проекта
mkdir -p ~/telegram-bot
cd ~/telegram-bot

# Копирование файлов проекта
# (скопируйте все файлы проекта в эту директорию)
```

### 3. Настройка виртуального окружения

```bash
# Создание виртуального окружения
python3 -m venv venv

# Активация виртуального окружения
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### 4. Настройка конфигурации

```bash
# Создание .env файла
nano .env
```

Содержимое `.env` файла:
```env
# Telegram Bot Configuration
BOT_TOKEN=ваш_токен_бота

# Database Configuration
DATABASE_PATH=database.db

# Admin User IDs (comma-separated)
ADMIN_USER_IDS=170481504,7631971482
```

### 5. Настройка прав доступа

```bash
# Установка правильных прав на файлы
chmod 600 .env
chmod +x bot.py
chown -R telegram-bot:telegram-bot ~/telegram-bot
```

## 🐧 Создание systemd сервиса (Linux)

### 1. Создание сервисного файла

```bash
sudo nano /etc/systemd/system/telegram-bot.service
```

Содержимое файла:
```ini
[Unit]
Description=Telegram Bot Service
After=network.target

[Service]
Type=simple
User=telegram-bot
Group=telegram-bot
WorkingDirectory=/home/telegram-bot/telegram-bot
Environment=PATH=/home/telegram-bot/telegram-bot/venv/bin
ExecStart=/home/telegram-bot/telegram-bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Запуск сервиса

```bash
# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение автозапуска
sudo systemctl enable telegram-bot

# Запуск сервиса
sudo systemctl start telegram-bot

# Проверка статуса
sudo systemctl status telegram-bot
```

## 🪟 Установка на Windows Server

### 1. Установка Python

```powershell
# Скачайте Python с python.org
# Установите с опцией "Add to PATH"
```

### 2. Создание виртуального окружения

```powershell
# Создание директории проекта
mkdir C:\telegram-bot
cd C:\telegram-bot

# Создание виртуального окружения
python -m venv venv

# Активация виртуального окружения
venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt
```

### 3. Создание .env файла

```powershell
# Создание .env файла
notepad .env
```

### 4. Создание Windows Service

Используйте NSSM (Non-Sucking Service Manager):

```powershell
# Скачайте NSSM с nssm.cc
# Установите сервис
nssm install TelegramBot
nssm set TelegramBot Application C:\telegram-bot\venv\Scripts\python.exe
nssm set TelegramBot AppParameters C:\telegram-bot\bot.py
nssm set TelegramBot AppDirectory C:\telegram-bot
nssm start TelegramBot
```

## 🔍 Мониторинг и логи

### Просмотр логов

```bash
# Linux (systemd)
sudo journalctl -u telegram-bot -f

# Просмотр последних 100 строк
sudo journalctl -u telegram-bot -n 100
```

### Проверка работы бота

```bash
# Проверка процесса
ps aux | grep bot.py

# Проверка портов (если используется)
netstat -tlnp | grep python
```

## 🔧 Обслуживание

### Обновление бота

```bash
# Остановка сервиса
sudo systemctl stop telegram-bot

# Обновление кода
# (скопируйте новые файлы)

# Перезапуск сервиса
sudo systemctl start telegram-bot
```

### Резервное копирование

```bash
# Создание резервной копии базы данных
cp database.db database_backup_$(date +%Y%m%d_%H%M%S).db

# Создание полной резервной копии
tar -czf telegram-bot-backup-$(date +%Y%m%d_%H%M%S).tar.gz ~/telegram-bot/
```

## 🚨 Устранение неполадок

### Частые проблемы

1. **Бот не запускается**
   ```bash
   # Проверьте токен бота
   python check_token.py
   
   # Проверьте логи
   sudo journalctl -u telegram-bot -n 50
   ```

2. **Ошибки базы данных**
   ```bash
   # Проверьте права доступа к файлу БД
   ls -la database.db
   
   # Пересоздайте БД
   rm database.db
   python -c "from database import Database; Database()"
   ```

3. **Проблемы с зависимостями**
   ```bash
   # Переустановите зависимости
   pip install -r requirements.txt --force-reinstall
   ```

### Полезные команды

```bash
# Проверка статуса сервиса
sudo systemctl status telegram-bot

# Перезапуск сервиса
sudo systemctl restart telegram-bot

# Остановка сервиса
sudo systemctl stop telegram-bot

# Просмотр логов в реальном времени
sudo journalctl -u telegram-bot -f

# Проверка использования ресурсов
htop
```

## 📊 Мониторинг производительности

### Настройка мониторинга

```bash
# Установка htop для мониторинга
sudo apt install htop -y

# Установка iotop для мониторинга диска
sudo apt install iotop -y
```

### Автоматический мониторинг

Создайте скрипт для проверки работы бота:

```bash
#!/bin/bash
# check_bot.sh

if ! systemctl is-active --quiet telegram-bot; then
    echo "Bot is not running, restarting..."
    sudo systemctl restart telegram-bot
    # Отправка уведомления администратору
fi
```

Добавьте в crontab:
```bash
# Проверка каждые 5 минут
*/5 * * * * /path/to/check_bot.sh
```

## 🔒 Безопасность

### Рекомендации по безопасности

1. **Ограничение доступа к файлам**
   ```bash
   chmod 600 .env
   chmod 644 *.py
   chmod 644 requirements.txt
   ```

2. **Настройка файрвола**
   ```bash
   # Блокировка всех входящих соединений кроме SSH
   sudo ufw default deny incoming
   sudo ufw default allow outgoing
   sudo ufw allow ssh
   sudo ufw enable
   ```

3. **Регулярные обновления**
   ```bash
   # Обновление системы
   sudo apt update && sudo apt upgrade -y
   
   # Обновление Python пакетов
   pip list --outdated
   pip install --upgrade package_name
   ```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи: `sudo journalctl -u telegram-bot -n 100`
2. Проверьте статус сервиса: `sudo systemctl status telegram-bot`
3. Проверьте конфигурацию: `python check_token.py`
4. Проверьте базу данных: `python -c "from database import Database; print('DB OK')"`

---

**Удачного развертывания! 🚀**
