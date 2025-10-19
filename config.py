import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Конфигурация бота
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_USER_IDS = [int(x) for x in os.getenv('ADMIN_USER_IDS', '').split(',') if x.strip()]  # Список ID администраторов

# Проверка обязательных переменных
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в переменных окружения!")

if not ADMIN_USER_IDS:
    raise ValueError("ADMIN_USER_IDS не установлены в переменных окружения!")

# Конфигурация базы данных
DATABASE_PATH = os.getenv('DATABASE_PATH', 'database.db')

# Сообщения
MESSAGES = {
    'welcome': 'Добро пожаловать! Выберите действие:',
    'application_start': '📝 Пожалуйста, введите ваше ФИО:',
    'application_phone': '📞 Теперь введите ваш номер телефона:\nПример: +7 (000) 000 00 00',
    'application_info': '💬 Расскажите, чем мы можем вам помочь?\nКакую мебель подбираете?\nКухня, шкаф, гардеробная?\n\nЕсть ли у вас уже проект мебели, или нужно спроектировать?',
    'application_success': '✅ Ваши данные сохранены! С вами свяжутся в ближайшее время.',
    'contact_manager': 'Для связи с менеджером/дизайнером напишите @username_manager',
    'admin_panel': 'Панель администратора',
    'no_applications': 'Заявок пока нет',
    'reminder': 'Вы начали оформлять заявку, но не завершили. Хотите продолжить?'
}

# Кнопки
BUTTONS = {
    'apply': 'Оформить заявку',
    'contact': 'Связаться с менеджером/дизайнером',
    'admin_panel': 'Админ-панель',
    'view_applications': 'Просмотр заявок',
    'view_inactive_users': 'Пользователи без заявок',
    'send_broadcast': 'Рассылка',
    'statistics': 'Статистика',
    'back': 'Назад',
    'cancel': 'Отмена'
}
