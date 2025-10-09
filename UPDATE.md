# 🔄 Инструкция по обновлению проекта на сервере

## 📋 Быстрое обновление

### 🚀 Автоматическое обновление (рекомендуется)

#### Для Linux/macOS:

```bash
# Сделать скрипт исполняемым
chmod +x update.sh

# Запуск скрипта обновления
./update.sh your-server-ip

# Или с указанием пользователя
./update.sh user@your-server-ip
```

#### Для Windows:

```powershell
# Запуск PowerShell скрипта
.\update.ps1 your-server-ip

# Или с указанием пользователя
.\update.ps1 user@your-server-ip
```

### 📋 Что делает скрипт автоматического обновления:

1. **Проверяет подключение** к серверу
2. **Останавливает сервис** telegram-bot
3. **Создает резервную копию** базы данных и конфигурации
4. **Копирует обновленные файлы** на сервер
5. **Обновляет зависимости** Python
6. **Настраивает права доступа** на файлы
7. **Перезагружает systemd** конфигурацию
8. **Запускает сервис** и проверяет его работу
9. **Показывает статус** и последние логи

## 🔧 Ручное обновление

### 1. Подключение к серверу

```bash
# Подключение по SSH
ssh user@your-server-ip

# Переход в директорию проекта
cd ~/telegram-bot
```

### 2. Остановка сервиса

```bash
# Остановка бота
sudo systemctl stop telegram-bot

# Проверка остановки
sudo systemctl status telegram-bot
```

### 3. Создание резервной копии

```bash
# Создание резервной копии базы данных
cp database.db database_backup_$(date +%Y%m%d_%H%M%S).db

# Создание резервной копии конфигурации
cp .env .env_backup_$(date +%Y%m%d_%H%M%S)

# Создание полной резервной копии проекта
tar -czf telegram-bot-backup-$(date +%Y%m%d_%H%M%S).tar.gz ~/telegram-bot/
```

### 4. Обновление кода

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

### 5. Обновление зависимостей

```bash
# Активация виртуального окружения
source venv/bin/activate

# Обновление зависимостей
pip install -r requirements.txt --upgrade

# Проверка установленных пакетов
pip list
```

### 6. Проверка конфигурации

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

### 7. Запуск сервиса

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

## 🔍 Проверка успешности обновления

### 1. Проверка статуса сервиса

```bash
# Статус сервиса
sudo systemctl status telegram-bot

# Проверка активности
sudo systemctl is-active telegram-bot

# Проверка автозапуска
sudo systemctl is-enabled telegram-bot
```

### 2. Проверка логов

```bash
# Последние логи
sudo journalctl -u telegram-bot -n 50

# Логи в реальном времени
sudo journalctl -u telegram-bot -f

# Логи за последний час
sudo journalctl -u telegram-bot --since "1 hour ago"
```

### 3. Проверка работы бота

```bash
# Проверка процесса
ps aux | grep bot.py

# Проверка использования ресурсов
htop

# Проверка сетевых соединений
netstat -tlnp | grep python
```

### 4. Тестирование функциональности

```bash
# Проверка базы данных
python3 -c "from database import Database; db = Database(); print('Database OK')"

# Проверка конфигурации
python3 -c "from config import BOT_TOKEN, ADMIN_USER_IDS; print('Config OK')"

# Проверка токена бота
python3 -c "from config import BOT_TOKEN; print('Bot token:', BOT_TOKEN[:10] + '...')"
```

## 🚨 Откат изменений (если что-то пошло не так)

### 1. Остановка сервиса

```bash
sudo systemctl stop telegram-bot
```

### 2. Восстановление из резервной копии

```bash
# Восстановление базы данных
cp database_backup_YYYYMMDD_HHMMSS.db database.db

# Восстановление конфигурации
cp .env_backup_YYYYMMDD_HHMMSS .env

# Или полное восстановление проекта
tar -xzf telegram-bot-backup-YYYYMMDD_HHMMSS.tar.gz
```

### 3. Перезапуск сервиса

```bash
sudo systemctl start telegram-bot
sudo systemctl status telegram-bot
```

## 📊 Мониторинг после обновления

### 1. Настройка автоматического мониторинга

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

### 2. Настройка уведомлений

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

## 🔧 Полезные команды для обновления

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

## 📝 Чек-лист обновления

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

## 🆘 Устранение неполадок

### Частые проблемы при обновлении

1. **Сервис не запускается после обновления**
   ```bash
   # Проверьте логи
   sudo journalctl -u telegram-bot -n 50
   
   # Проверьте конфигурацию
   python3 -c "from config import *; print('Config OK')"
   
   # Проверьте зависимости
   pip list
   ```

2. **Ошибки базы данных**
   ```bash
   # Проверьте права доступа к файлу БД
   ls -la database.db
   
   # Восстановите из резервной копии
   cp database_backup_*.db database.db
   ```

3. **Проблемы с зависимостями**
   ```bash
   # Переустановите зависимости
   pip install -r requirements.txt --force-reinstall
   
   # Проверьте виртуальное окружение
   which python
   pip --version
   ```

4. **Проблемы с правами доступа**
   ```bash
   # Установите правильные права
   chmod 600 .env
   chmod 644 *.py
   chmod +x bot.py
   
   # Проверьте владельца файлов
   ls -la
   ```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи: `sudo journalctl -u telegram-bot -n 100`
2. Проверьте статус сервиса: `sudo systemctl status telegram-bot`
3. Проверьте конфигурацию: `python3 -c "from config import *; print('Config OK')"`
4. Проверьте базу данных: `python3 -c "from database import Database; print('DB OK')"`
5. Проверьте зависимости: `pip list`

---

**Удачного обновления! 🚀**
