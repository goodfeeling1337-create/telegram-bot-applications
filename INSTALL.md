# 🚀 Установка Telegram бота через консоль

## 📋 Быстрая установка

### 1. Клонирование проекта
```bash
git clone <repository_url>
cd KworkProject
```

### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 3. Настройка конфигурации
```bash
# Создать .env файл
nano .env
```

Добавить в .env:
```env
BOT_TOKEN=ваш_токен_бота
ADMIN_USER_IDS=170481504,7631971482,8438177540
DATABASE_PATH=database.db
```

### 4. Запуск бота
```bash
python bot.py
```

---

## 🖥️ Установка на сервер

### 1. Подключение к серверу
```bash
ssh user@server_ip
```

### 2. Клонирование проекта
```bash
git clone <repository_url>
cd KworkProject
```

### 3. Установка Python и зависимостей
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv -y

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Настройка конфигурации
```bash
nano .env
```

### 5. Создание systemd сервиса
```bash
sudo nano /etc/systemd/system/telegram-bot.service
```

Содержимое:
```ini
[Unit]
Description=Telegram Bot Service
After=network.target

[Service]
Type=simple
User=user
Group=user
WorkingDirectory=/home/user/KworkProject
Environment=PATH=/home/user/KworkProject/venv/bin
ExecStart=/home/user/KworkProject/venv/bin/python /home/user/KworkProject/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 6. Запуск сервиса
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

### 7. Проверка работы
```bash
sudo systemctl status telegram-bot
sudo journalctl -u telegram-bot -f
```

---

## 🔧 Управление сервисом

### Основные команды
```bash
# Статус
sudo systemctl status telegram-bot

# Запуск
sudo systemctl start telegram-bot

# Остановка
sudo systemctl stop telegram-bot

# Перезапуск
sudo systemctl restart telegram-bot

# Логи
sudo journalctl -u telegram-bot -f
```

### Обновление бота
```bash
cd KworkProject
git pull
sudo systemctl restart telegram-bot
```

---

## 📝 Получение токена бота

1. Найдите @BotFather в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Скопируйте токен в .env файл

## 📝 Получение ID администратора

1. Найдите @userinfobot в Telegram
2. Отправьте любое сообщение
3. Скопируйте ваш ID в .env файл

---

## ❗ Устранение неполадок

### Бот не запускается
```bash
# Проверьте логи
sudo journalctl -u telegram-bot -n 50

# Проверьте токен
python3 -c "from config import BOT_TOKEN; print('OK' if BOT_TOKEN else 'ERROR')"
```

### Ошибки базы данных
```bash
# Проверьте права доступа
ls -la database.db

# Пересоздайте БД
rm database.db
python3 -c "from database import Database; Database()"
```

### Проблемы с зависимостями
```bash
# Переустановите зависимости
pip install -r requirements.txt --force-reinstall
```

---

## 🎯 Готово!

После выполнения всех шагов бот будет работать на сервере и автоматически запускаться при перезагрузке.
