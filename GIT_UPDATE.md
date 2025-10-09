# 🔄 Инструкция по обновлению проекта через Git

## 📋 Быстрое обновление через Git

### 🚀 Автоматическое обновление (рекомендуется)

#### Для Linux/macOS:

```bash
# Сделать скрипт исполняемым
chmod +x git-update.sh

# Запуск скрипта обновления через Git
./git-update.sh your-server-ip

# Или с указанием пользователя и репозитория
./git-update.sh user@your-server-ip https://github.com/your-username/your-repo.git
```

#### Для Windows:

```powershell
# Запуск PowerShell скрипта
.\git-update.ps1 your-server-ip

# Или с указанием пользователя и репозитория
.\git-update.ps1 user@your-server-ip https://github.com/your-username/your-repo.git
```

### 📋 Что делает скрипт автоматического обновления через Git:

1. ✅ **Проверяет подключение** к серверу
2. ✅ **Проверяет Git репозиторий** (клонирует если нужно)
3. ✅ **Останавливает сервис** telegram-bot
4. ✅ **Создает резервную копию** базы данных и конфигурации
5. ✅ **Получает изменения** из Git репозитория (`git fetch`)
6. ✅ **Показывает изменения** которые будут применены
7. ✅ **Обновляет код** через `git pull origin main`
8. ✅ **Обновляет зависимости** Python
9. ✅ **Настраивает права доступа** на файлы
10. ✅ **Перезагружает systemd** конфигурацию
11. ✅ **Запускает сервис** и проверяет его работу
12. ✅ **Показывает статус** и последние логи

## 🔧 Ручное обновление через Git

### 1. Подключение к серверу

```bash
# Подключение по SSH
ssh user@your-server-ip

# Переход в директорию проекта
cd ~/telegram-bot
```

### 2. Проверка Git репозитория

```bash
# Проверка статуса Git
git status

# Проверка удаленного репозитория
git remote -v

# Если репозиторий не настроен, добавьте его:
git remote add origin https://github.com/goodfeeling1337-create/telegram-bot-applications.git
```

### 3. Остановка сервиса

```bash
# Остановка бота
sudo systemctl stop telegram-bot

# Проверка остановки
sudo systemctl status telegram-bot
```

### 4. Создание резервной копии

```bash
# Создание резервной копии базы данных
cp database.db database_backup_$(date +%Y%m%d_%H%M%S).db

# Создание резервной копии конфигурации
cp .env .env_backup_$(date +%Y%m%d_%H%M%S)

# Создание полной резервной копии проекта
tar -czf telegram-bot-backup-$(date +%Y%m%d_%H%M%S).tar.gz ~/telegram-bot/
```

### 5. Получение изменений из Git

```bash
# Получение последних изменений
git fetch origin

# Просмотр изменений
git log HEAD..origin/main --oneline

# Просмотр детальных изменений
git diff HEAD..origin/main

# Просмотр измененных файлов
git diff --name-only HEAD..origin/main
```

### 6. Обновление до последней версии

```bash
# Обновление до последней версии
git pull origin main

# Проверка статуса
git status

# Просмотр последнего коммита
git log -1 --oneline
```

### 7. Обновление зависимостей

```bash
# Активация виртуального окружения
source venv/bin/activate

# Обновление зависимостей
pip install -r requirements.txt --upgrade

# Проверка установленных пакетов
pip list
```

### 8. Проверка конфигурации

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

### 9. Запуск сервиса

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

### 4. Проверка Git статуса

```bash
# Текущая версия
git log -1 --oneline

# Статус репозитория
git status

# История последних коммитов
git log --oneline -5

# Проверка ветки
git branch -a
```

### 5. Тестирование функциональности

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

### 2. Откат через Git

```bash
# Просмотр истории коммитов
git log --oneline -10

# Откат к предыдущему коммиту
git reset --hard HEAD~1

# Или откат к конкретному коммиту
git reset --hard <commit-hash>

# Принудительное обновление удаленного репозитория (если нужно)
git push origin main --force
```

### 3. Восстановление из резервной копии

```bash
# Восстановление базы данных
cp database_backup_YYYYMMDD_HHMMSS.db database.db

# Восстановление конфигурации
cp .env_backup_YYYYMMDD_HHMMSS .env

# Или полное восстановление проекта
tar -xzf telegram-bot-backup-YYYYMMDD_HHMMSS.tar.gz
```

### 4. Перезапуск сервиса

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

### 2. Настройка уведомлений о новых версиях

```bash
# Создание скрипта для проверки обновлений
cat > check_updates.sh << 'EOF'
#!/bin/bash
cd ~/telegram-bot
git fetch origin
if [ $(git rev-list HEAD...origin/main --count) -gt 0 ]; then
    echo "$(date): New updates available" >> /var/log/bot-updates.log
    # Отправка уведомления администратору
    # curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/sendMessage" \
    #      -d "chat_id=<ADMIN_CHAT_ID>&text=New bot updates available"
fi
EOF

chmod +x check_updates.sh

# Добавление в crontab (проверка каждый час)
echo "0 * * * * /path/to/check_updates.sh" | crontab -
```

## 🔧 Полезные команды для работы с Git

```bash
# Проверка статуса репозитория
git status

# Просмотр истории коммитов
git log --oneline -10

# Просмотр изменений в файлах
git diff

# Просмотр изменений конкретного файла
git diff HEAD~1 config.py

# Просмотр информации о коммите
git show HEAD

# Просмотр веток
git branch -a

# Переключение на другую ветку
git checkout branch-name

# Создание новой ветки
git checkout -b new-feature

# Слияние веток
git merge branch-name

# Отмена изменений в рабочей директории
git checkout -- filename

# Отмена индексации файла
git reset HEAD filename

# Просмотр удаленного репозитория
git remote -v

# Изменение URL удаленного репозитория
git remote set-url origin new-url

# Клонирование репозитория
git clone https://github.com/username/repo.git

# Добавление удаленного репозитория
git remote add origin https://github.com/username/repo.git
```

## 📝 Чек-лист обновления через Git

- [ ] Подключение к серверу установлено
- [ ] Git репозиторий настроен
- [ ] Сервис остановлен
- [ ] Резервная копия создана
- [ ] Изменения получены (`git fetch`)
- [ ] Изменения просмотрены (`git log`)
- [ ] Код обновлен (`git pull`)
- [ ] Зависимости обновлены
- [ ] Конфигурация проверена
- [ ] Права доступа установлены
- [ ] Сервис запущен
- [ ] Статус сервиса проверен
- [ ] Логи проверены
- [ ] Git статус проверен
- [ ] Функциональность протестирована
- [ ] Мониторинг настроен

## 🆘 Устранение неполадок

### Частые проблемы при обновлении через Git

1. **Конфликты при слиянии**
   ```bash
   # Просмотр конфликтов
   git status
   
   # Разрешение конфликтов вручную
   nano conflicted-file.py
   
   # Добавление разрешенных файлов
   git add resolved-file.py
   
   # Завершение слияния
   git commit
   ```

2. **Локальные изменения мешают обновлению**
   ```bash
   # Сохранение локальных изменений
   git stash
   
   # Обновление
   git pull origin main
   
   # Восстановление локальных изменений
   git stash pop
   ```

3. **Проблемы с правами доступа к репозиторию**
   ```bash
   # Проверка URL репозитория
   git remote -v
   
   # Обновление URL
   git remote set-url origin https://github.com/username/repo.git
   
   # Проверка подключения
   git fetch origin
   ```

4. **Сервис не запускается после обновления**
   ```bash
   # Проверьте логи
   sudo journalctl -u telegram-bot -n 50
   
   # Проверьте конфигурацию
   python3 -c "from config import *; print('Config OK')"
   
   # Проверьте зависимости
   pip list
   ```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи: `sudo journalctl -u telegram-bot -n 100`
2. Проверьте статус сервиса: `sudo systemctl status telegram-bot`
3. Проверьте Git статус: `git status`
4. Проверьте конфигурацию: `python3 -c "from config import *; print('Config OK')"`
5. Проверьте базу данных: `python3 -c "from database import Database; print('DB OK')"`
6. Проверьте зависимости: `pip list`

---

**Удачного обновления через Git! 🚀**
