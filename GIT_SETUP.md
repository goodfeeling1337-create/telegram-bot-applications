# 📤 Загрузка проекта в Git

## 🚀 Быстрая загрузка

### 1. Создание репозитория на GitHub/GitLab

1. Зайдите на [GitHub](https://github.com) или [GitLab](https://gitlab.com)
2. Нажмите "New repository" или "Создать проект"
3. Назовите репозиторий: `telegram-bot-applications`
4. Выберите "Public" или "Private"
5. **НЕ** добавляйте README, .gitignore или лицензию (уже есть)
6. Нажмите "Create repository"

### 2. Подключение к удаленному репозиторию

```bash
# Добавить удаленный репозиторий
git remote add origin https://github.com/ваш_username/telegram-bot-applications.git

# Загрузить код
git push -u origin master
```

### 3. Альтернативный способ (если репозиторий уже создан)

```bash
# Клонировать существующий репозиторий
git clone https://github.com/ваш_username/telegram-bot-applications.git
cd telegram-bot-applications

# Скопировать файлы проекта
cp -r /path/to/KworkProject/* .

# Добавить и загрузить
git add .
git commit -m "Add Telegram bot application"
git push
```

---

## 📋 Инструкция для пользователей

### Установка с GitHub

```bash
# Клонирование
git clone https://github.com/ваш_username/telegram-bot-applications.git
cd telegram-bot-applications

# Автоматическая установка
chmod +x install.sh
./install.sh

# Настройка
nano .env

# Запуск
python bot.py
```

### Установка с GitLab

```bash
# Клонирование
git clone https://gitlab.com/ваш_username/telegram-bot-applications.git
cd telegram-bot-applications

# Автоматическая установка
chmod +x install.sh
./install.sh

# Настройка
nano .env

# Запуск
python bot.py
```

---

## 🔧 Управление репозиторием

### Обновление кода

```bash
# Скачать изменения
git pull

# Загрузить изменения
git add .
git commit -m "Описание изменений"
git push
```

### Создание релиза

```bash
# Создать тег
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

---

## 📝 Готовые команды для копирования

### Создание репозитория на GitHub:
1. Перейдите на https://github.com/new
2. Название: `telegram-bot-applications`
3. Описание: `Telegram bot for collecting applications with admin panel`
4. Выберите Public/Private
5. Нажмите "Create repository"

### Подключение и загрузка:
```bash
git remote add origin https://github.com/ваш_username/telegram-bot-applications.git
git branch -M main
git push -u origin main
```

---

## ✅ Готово!

После загрузки в Git любой пользователь сможет установить бота одной командой:

```bash
git clone https://github.com/ваш_username/telegram-bot-applications.git
cd telegram-bot-applications
./install.sh
```
