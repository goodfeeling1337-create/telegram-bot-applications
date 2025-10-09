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
ADMIN_USER_IDS=170481504,7631971482,8438177540
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

## 🔄 Инструкция по обновлению проекта на сервере

### 🚀 Автоматическое обновление (рекомендуется)

#### Для Linux/macOS:

```bash
# Запуск скрипта автоматического обновления
./deploy.sh your-server-ip

# Или с указанием пользователя
./deploy.sh user@your-server-ip
```

#### Для Windows:

```powershell
# Запуск PowerShell скрипта
.\deploy.ps1 your-server-ip

# Или с указанием пользователя
.\deploy.ps1 user@your-server-ip
```

### 📋 Ручное обновление

#### 1. Подключение к серверу

```bash
# Подключение по SSH
ssh user@your-server-ip

# Переход в директорию проекта
cd ~/telegram-bot
```

#### 2. Остановка сервиса

```bash
# Остановка бота
sudo systemctl stop telegram-bot

# Проверка остановки
sudo systemctl status telegram-bot
```

#### 3. Создание резервной копии

```bash
# Создание резервной копии базы данных
cp database.db database_backup_$(date +%Y%m%d_%H%M%S).db

# Создание резервной копии конфигурации
cp .env .env_backup_$(date +%Y%m%d_%H%M%S)

# Создание полной резервной копии проекта
tar -czf telegram-bot-backup-$(date +%Y%m%d_%H%M%S).tar.gz ~/telegram-bot/
```

#### 4. Обновление кода

**Вариант A: Через Git (если проект в Git репозитории)**

```bash
# Получение последних изменений
git fetch origin

# Просмотр изменений
git log HEAD..origin/main --oneline

# Обновление до последней версии
git pull origin main

# Проверка статуса
git status
```

**Вариант B: Ручное копирование файлов**

```bash
# Скачивание новых файлов (замените на ваши пути)
# scp user@local-machine:/path/to/project/* ./

# Или загрузка через wget/curl
# wget https://your-repo.com/latest-release.tar.gz
# tar -xzf latest-release.tar.gz
```

#### 5. Обновление зависимостей

```bash
# Активация виртуального окружения
source venv/bin/activate

# Обновление зависимостей
pip install -r requirements.txt --upgrade

# Проверка установленных пакетов
pip list
```

#### 6. Проверка конфигурации

```bash
# Проверка .env файла
cat .env

# Проверка прав доступа
ls -la .env
ls -la *.py

# Установка правильных прав
chmod 600 .env
chmod 644 *.py
chmod +x bot.py
```

#### 7. Запуск сервиса

```bash
# Перезагрузка systemd
sudo systemctl daemon-reload

# Запуск сервиса
sudo systemctl start telegram-bot

# Проверка статуса
sudo systemctl status telegram-bot

# Просмотр логов
sudo journalctl -u telegram-bot -f
```

### 🔍 Проверка успешности обновления

#### 1. Проверка статуса сервиса

```bash
# Статус сервиса
sudo systemctl status telegram-bot

# Проверка активности
sudo systemctl is-active telegram-bot

# Проверка автозапуска
sudo systemctl is-enabled telegram-bot
```

#### 2. Проверка логов

```bash
# Последние логи
sudo journalctl -u telegram-bot -n 50

# Логи в реальном времени
sudo journalctl -u telegram-bot -f

# Логи за последний час
sudo journalctl -u telegram-bot --since "1 hour ago"
```

#### 3. Проверка работы бота

```bash
# Проверка процесса
ps aux | grep bot.py

# Проверка использования ресурсов
htop

# Проверка сетевых соединений
netstat -tlnp | grep python
```

#### 4. Тестирование функциональности

```bash
# Проверка базы данных
python3 -c "from database import Database; db = Database(); print('Database OK')"

# Проверка конфигурации
python3 -c "from config import BOT_TOKEN, ADMIN_USER_IDS; print('Config OK')"

# Проверка токена бота
python3 -c "from config import BOT_TOKEN; print('Bot token:', BOT_TOKEN[:10] + '...')"
```

### 🚨 Откат изменений (если что-то пошло не так)

#### 1. Остановка сервиса

```bash
sudo systemctl stop telegram-bot
```

#### 2. Восстановление из резервной копии

```bash
# Восстановление базы данных
cp database_backup_YYYYMMDD_HHMMSS.db database.db

# Восстановление конфигурации
cp .env_backup_YYYYMMDD_HHMMSS .env

# Или полное восстановление проекта
tar -xzf telegram-bot-backup-YYYYMMDD_HHMMSS.tar.gz
```

#### 3. Перезапуск сервиса

```bash
sudo systemctl start telegram-bot
sudo systemctl status telegram-bot
```

### 📊 Мониторинг после обновления

#### 1. Настройка автоматического мониторинга

```bash
# Создание скрипта мониторинга
cat > check_bot.sh << 'EOF'
#!/bin/bash
if ! systemctl is-active --quiet telegram-bot; then
    echo "$(date): Bot is not running, restarting..." >> /var/log/bot-monitor.log
    sudo systemctl restart telegram-bot
    # Отправка уведомления (опционально)
    # curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/sendMessage" \
    #      -d "chat_id=<ADMIN_CHAT_ID>&text=Bot restarted on server"
fi
EOF

chmod +x check_bot.sh

# Добавление в crontab
echo "*/5 * * * * /path/to/check_bot.sh" | crontab -
```

#### 2. Настройка уведомлений

```bash
# Создание скрипта для отправки уведомлений
cat > notify_admin.sh << 'EOF'
#!/bin/bash
BOT_TOKEN="your_bot_token"
ADMIN_CHAT_ID="your_admin_chat_id"
MESSAGE="$1"

curl -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
     -d "chat_id=${ADMIN_CHAT_ID}&text=${MESSAGE}"
EOF

chmod +x notify_admin.sh
```

### 🔧 Полезные команды для обновления

```bash
# Проверка версии Python
python3 --version

# Проверка установленных пакетов
pip list

# Проверка свободного места
df -h

# Проверка использования памяти
free -h

# Проверка загрузки системы
uptime

# Проверка сетевых соединений
ss -tlnp

# Проверка логов системы
journalctl --since "1 hour ago" | grep telegram-bot
```

### 📝 Чек-лист обновления

- [ ] Создана резервная копия базы данных
- [ ] Создана резервная копия конфигурации
- [ ] Сервис остановлен
- [ ] Код обновлен
- [ ] Зависимости обновлены
- [ ] Конфигурация проверена
- [ ] Права доступа установлены
- [ ] Сервис запущен
- [ ] Статус сервиса проверен
- [ ] Логи проверены
- [ ] Функциональность протестирована
- [ ] Мониторинг настроен

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
