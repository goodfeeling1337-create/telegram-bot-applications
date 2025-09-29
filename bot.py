import asyncio
import logging
import re
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ParseMode

from config import BOT_TOKEN, ADMIN_USER_IDS, MESSAGES, BUTTONS
from database import Database

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация базы данных
db = Database()

class TelegramBot:
    def __init__(self):
        self.application = None
        self.db = Database()
    
    def is_admin(self, user_id: int) -> bool:
        """Проверка, является ли пользователь администратором"""
        return user_id in ADMIN_USER_IDS
    
    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать главное меню"""
        user = update.effective_user
        
        # Создаем клавиатуру
        keyboard = [
            [KeyboardButton(BUTTONS['apply'])]
        ]
        
        if self.is_admin(user.id):
            keyboard.append([KeyboardButton(BUTTONS['admin_panel'])])
        
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            MESSAGES['welcome'],
            reply_markup=reply_markup
        )
    
    async def show_main_menu_silent(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать главное меню без приветственного сообщения"""
        user = update.effective_user
        
        # Создаем клавиатуру
        keyboard = [
            [KeyboardButton(BUTTONS['apply'])]
        ]
        
        if self.is_admin(user.id):
            keyboard.append([KeyboardButton(BUTTONS['admin_panel'])])
        
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "Выберите действие:",
            reply_markup=reply_markup
        )
    
    async def show_main_menu_with_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message: str):
        """Показать главное меню с кастомным сообщением"""
        user = update.effective_user
        
        # Создаем клавиатуру
        keyboard = [
            [KeyboardButton(BUTTONS['apply'])]
        ]
        
        if self.is_admin(user.id):
            keyboard.append([KeyboardButton(BUTTONS['admin_panel'])])
        
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            message,
            reply_markup=reply_markup
        )
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        
        # Добавляем пользователя в базу данных
        self.db.add_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        # Очищаем состояние пользователя
        self.db.clear_user_state(user.id)
        
        # Показываем главное меню
        await self.show_main_menu(update, context)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        user = update.effective_user
        text = update.message.text
        
        # Проверяем, является ли пользователь администратором
        is_admin = self.is_admin(user.id)
        
        # Проверяем состояние пользователя для рассылки
        state_data = self.db.get_user_state(user.id)
        if state_data and state_data['state'] == 'broadcast_message':
            await self.send_broadcast_message(update, context)
            return
        
        # Обработка кнопок
        if text == BUTTONS['apply']:
            await self.start_application(update, context)
        elif text == BUTTONS['admin_panel'] and is_admin:
            await self.admin_panel(update, context)
        elif text == "📊 Статистика" and is_admin:
            await self.show_statistics(update, context)
        elif text == "📨 Рассылка" and is_admin:
            await self.start_broadcast(update, context)
        elif text == "📋 Все заявки" and is_admin:
            await self.view_applications(update, context)
        elif text == "👥 Все пользователи" and is_admin:
            await self.view_inactive_users(update, context)
        elif text == "🗑️ Удалить заявку" and is_admin:
            await self.start_delete_application(update, context)
        else:
            # Проверяем состояние пользователя для обработки формы заявки
            state_data = self.db.get_user_state(user.id)
            if state_data and state_data['state'] in ['application_fio', 'application_phone', 'application_info', 'delete_application']:
                await self.handle_application_state(update, context)
            else:
                # Обработка случайных сообщений
                await self.handle_random_message(update, context)
    
    async def start_application(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало оформления заявки"""
        user = update.effective_user
        
        # Очищаем предыдущее состояние
        self.db.clear_user_state(user.id)
        
        # Сохраняем состояние пользователя
        self.db.save_user_state(user.id, 'application_fio')
        
        await update.message.reply_text(MESSAGES['application_start'])
    
    async def handle_application_state(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка состояний формы заявки"""
        user = update.effective_user
        text = update.message.text
        
        # Получаем текущее состояние пользователя
        state_data = self.db.get_user_state(user.id)
        if not state_data:
            return
        
        state = state_data['state']
        
        if state == 'application_fio':
            # Сохраняем ФИО и переходим к телефону
            if text and len(text.strip()) > 0:
                import json
                data = {'fio': text.strip()}
                self.db.save_user_state(user.id, 'application_phone', json.dumps(data))
                await update.message.reply_text(MESSAGES['application_phone'])
            else:
                await update.message.reply_text("Пожалуйста, введите ваше ФИО:")
        
        elif state == 'application_phone':
            # Валидация номера телефона
            if self.validate_phone(text):
                import json
                # Получаем ФИО из предыдущего состояния
                fio_data = json.loads(state_data['data']) if state_data['data'] else {}
                data = {
                    'fio': fio_data.get('fio', user.first_name or user.username or "Пользователь"), 
                    'phone': text.strip()
                }
                self.db.save_user_state(user.id, 'application_info', json.dumps(data))
                await update.message.reply_text(MESSAGES['application_info'])
            else:
                await update.message.reply_text(
                    "Пожалуйста, введите корректный номер телефона (например: +7 (999) 123 45 67 или +7 999 123 45 67)"
                )
        
        elif state == 'application_info':
            # Завершаем оформление заявки
            if text and len(text.strip()) > 0:
                await self.complete_application(update, context, text.strip())
            else:
                await update.message.reply_text("Пожалуйста, опишите ваши потребности:")
        
        elif state == 'delete_application':
            # Обработка удаления заявки
            await self.handle_delete_application(update, context, text)
        
        elif state.startswith('reply_application_'):
            # Обработка ответа на заявку
            await self.handle_reply_message(update, context, text, state)
    
    async def handle_random_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка случайных сообщений"""
        user = update.effective_user
        
        # Очищаем состояние пользователя
        self.db.clear_user_state(user.id)
        
        # Показываем стартовое меню с сообщением о случайном вводе
        await self.show_main_menu_with_message(update, context, "❓ Не нашёл подходящий вариант. Открою стартовое меню 📋")
    
    async def handle_reply_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, state: str):
        """Обработка ответа на заявку"""
        user = update.effective_user
        
        if not self.is_admin(user.id):
            return
        
        # Извлекаем ID заявки из состояния
        app_id = int(state.split('_')[-1])
        
        # Получаем данные заявки
        applications = self.db.get_applications()
        app = next((a for a in applications if a['id'] == app_id), None)
        
        if not app:
            await update.message.reply_text("❌ Заявка не найдена.")
            return
        
        # Получаем telegram_id пользователя
        user_data = self.db.get_user_by_id(app['user_id'])
        telegram_id = user_data.get('telegram_id')
        
        if not telegram_id:
            await update.message.reply_text("❌ Не удалось найти пользователя для отправки ответа.")
            return
        
        # Отправляем ответ пользователю
        try:
            await context.bot.send_message(
                chat_id=telegram_id,
                text=f"💬 **Ответ от администратора на вашу заявку #{app_id}:**\n\n{text}",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Меняем статус заявки на "Выполнена"
            success = self.db.update_application_status(app_id, 'Выполнена')
            if success:
                logger.info(f"Статус заявки {app_id} изменен на 'Выполнена'")
            else:
                logger.warning(f"Не удалось изменить статус заявки {app_id}")
            
            await update.message.reply_text(f"✅ Ответ отправлен пользователю заявки #{app_id}. Статус изменен на 'Выполнена'.")
            
            # Очищаем состояние
            self.db.clear_user_state(user.id)
            
            # Возвращаемся в админ-меню
            await asyncio.sleep(2)
            await self.admin_panel(update, context)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка отправки ответа: {e}")
            # Очищаем состояние даже при ошибке
            self.db.clear_user_state(user.id)
    
    async def handle_delete_application(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Обработка удаления заявки"""
        user = update.effective_user
        
        if not self.is_admin(user.id):
            return
        
        try:
            # Пытаемся получить номер заявки
            app_id = int(text.strip())
            
            # Проверяем, существует ли заявка
            applications = self.db.get_applications()
            if not any(app['id'] == app_id for app in applications):
                await update.message.reply_text("❌ Заявка с таким номером не найдена.")
                return
            
            # Удаляем заявку
            success = self.db.delete_application(app_id)
            
            if success:
                await update.message.reply_text(f"✅ Заявка #{app_id} успешно удалена!")
            else:
                await update.message.reply_text("❌ Ошибка при удалении заявки.")
            
            # Очищаем состояние пользователя
            self.db.clear_user_state(user.id)
            
        except ValueError:
            await update.message.reply_text("❌ Пожалуйста, введите корректный номер заявки (только цифры).")
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик callback-кнопок"""
        query = update.callback_query
        user = update.effective_user
        
        if not self.is_admin(user.id):
            await query.answer("У вас нет прав доступа к этой функции.")
            return
        
        await query.answer()
        
        data = query.data
        
        if data == "cancel_broadcast":
            await self.handle_cancel_broadcast(update, context)
            return
        
        action, app_id = data.split('_', 1)
        app_id = int(app_id)
        
        if action == "reply":
            await self.handle_reply_application(update, context, app_id)
        elif action == "complete":
            await self.handle_complete_application(update, context, app_id)
        elif action == "delete":
            await self.handle_delete_application_callback(update, context, app_id)
    
    async def handle_reply_application(self, update: Update, context: ContextTypes.DEFAULT_TYPE, app_id: int):
        """Обработка кнопки 'Ответить'"""
        query = update.callback_query
        
        # Сохраняем состояние для ответа на заявку
        self.db.save_user_state(update.effective_user.id, f'reply_application_{app_id}')
        
        await query.edit_message_text(
            f"💬 **Ответ на заявку #{app_id}**\n\nВведите ваш ответ:",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_complete_application(self, update: Update, context: ContextTypes.DEFAULT_TYPE, app_id: int):
        """Обработка кнопки 'Завершить'"""
        query = update.callback_query
        
        # Обновляем статус заявки на 'Выполнена'
        success = self.db.update_application_status(app_id, 'Выполнена')
        
        if success:
            await query.edit_message_text(
                f"✅ **Заявка #{app_id} завершена!**\n\nСтатус изменен на 'Выполнена'",
                parse_mode=ParseMode.MARKDOWN
            )
            # Возвращаемся в админ-меню
            await asyncio.sleep(2)
            await self.admin_panel(update, context)
        else:
            await query.answer("❌ Ошибка при обновлении статуса заявки.")
    
    async def handle_delete_application_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, app_id: int):
        """Обработка кнопки 'Удалить'"""
        query = update.callback_query
        
        # Удаляем заявку
        success = self.db.delete_application(app_id)
        
        if success:
            await query.edit_message_text(
                f"🗑️ **Заявка #{app_id} удалена!**",
                parse_mode=ParseMode.MARKDOWN
            )
            # Отправляем сообщение с панелью администратора
            await asyncio.sleep(1)
            await self.send_admin_panel_message(update, context)
        else:
            await query.answer("❌ Ошибка при удалении заявки.")
    
    async def complete_application(self, update: Update, context: ContextTypes.DEFAULT_TYPE, additional_info: str):
        """Завершение оформления заявки"""
        user = update.effective_user
        
        try:
            # Получаем данные из состояний
            phone_state = self.db.get_user_state(user.id)
            if not phone_state or phone_state['state'] != 'application_info':
                await update.message.reply_text("❌ Произошла ошибка. Начните оформление заявки заново.")
                return
            
            # Парсим данные из JSON
            import json
            try:
                data = json.loads(phone_state['data'])
                fio = data.get('fio', user.first_name or user.username or "Пользователь")
                phone = data.get('phone', '')
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Ошибка парсинга данных заявки: {e}")
                await update.message.reply_text("❌ Произошла ошибка. Начните оформление заявки заново.")
                return
            
            # Получаем данные пользователя
            user_data = self.db.get_user(user.id)
            if not user_data:
                await update.message.reply_text("❌ Пользователь не найден. Начните оформление заявки заново.")
                return
            
            # Сохраняем заявку
            success = self.db.add_application(
                user_id=user_data['id'],
                name=fio,
                phone=phone,
                additional_info=additional_info,
                status='Новая'
            )
            
            if success:
                # Получаем ID только что созданной заявки
                applications = self.db.get_applications()
                if applications:
                    new_app_id = max(app['id'] for app in applications)
                else:
                    new_app_id = 1
                
                # Очищаем состояние пользователя
                self.db.clear_user_state(user.id)
                
                # Уведомляем пользователя
                await update.message.reply_text("✅ " + MESSAGES['application_success'])
                
                # Уведомляем администратора с ID конкретной заявки
                await self.notify_admin_new_application(update, context, fio, phone, additional_info, new_app_id)
                
                # Показываем главное меню без приветственного сообщения
                await self.show_main_menu_silent(update, context)
                
                logger.info(f"Заявка успешно создана: ID={new_app_id}, ФИО={fio}, Телефон={phone}, Пользователь={user.id}")
            else:
                await update.message.reply_text("❌ Произошла ошибка при сохранении заявки. Попробуйте еще раз.")
                logger.error(f"Ошибка сохранения заявки для пользователя {user.id}")
                
        except Exception as e:
            logger.error(f"Ошибка в complete_application: {e}")
            await update.message.reply_text("❌ Произошла ошибка. Попробуйте еще раз.")
            # Очищаем состояние при ошибке
            self.db.clear_user_state(user.id)
    
    def validate_phone(self, phone: str) -> bool:
        """Валидация номера телефона"""
        if not phone:
            return False
        
        # Удаляем все символы кроме цифр и +
        clean_phone = re.sub(r'[^\d+]', '', phone)
        
        # Проверяем различные форматы российских номеров
        patterns = [
            r'^\+7\d{10}$',  # +7XXXXXXXXXX
            r'^8\d{10}$',    # 8XXXXXXXXXX
            r'^7\d{10}$',    # 7XXXXXXXXXX
        ]
        
        # Проверяем исходный формат с пробелами и скобками
        original_patterns = [
            r'^\+7\s*\(\d{3}\)\s*\d{3}\s*\d{2}\s*\d{2}$',  # +7 (XXX) XXX XX XX
            r'^\+7\s*\d{3}\s*\d{3}\s*\d{2}\s*\d{2}$',      # +7 XXX XXX XX XX
            r'^8\s*\d{3}\s*\d{3}\s*\d{2}\s*\d{2}$',        # 8 XXX XXX XX XX
        ]
        
        # Проверяем очищенный номер
        clean_valid = any(re.match(pattern, clean_phone) for pattern in patterns)
        
        # Проверяем исходный формат
        original_valid = any(re.match(pattern, phone.strip()) for pattern in original_patterns)
        
        return clean_valid or original_valid
    
    def escape_markdown(self, text: str) -> str:
        """Экранирование специальных символов Markdown"""
        if not text:
            return text
        # Экранируем специальные символы Markdown
        escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in escape_chars:
            text = text.replace(char, f'\\{char}')
        return text
    
    async def send_admin_panel_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отправка сообщения с панелью администратора"""
        user = update.effective_user
        
        if not self.is_admin(user.id):
            return
        
        keyboard = [
            [KeyboardButton("📊 Статистика"), KeyboardButton("📨 Рассылка")],
            [KeyboardButton("📋 Все заявки"), KeyboardButton("👥 Все пользователи")],
            [KeyboardButton("🗑️ Удалить заявку")]
        ]
        
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        # Отправляем новое сообщение с панелью администратора
        logger.info(f"send_admin_panel_message: отправляем в чат {update.effective_chat.id}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🔧 **Панель администратора**\n\nВыберите действие:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def admin_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Панель администратора"""
        user = update.effective_user
        
        if not self.is_admin(user.id):
            if update.message:
                await update.message.reply_text("У вас нет прав доступа к админ-панели.")
            return
        
        keyboard = [
            [KeyboardButton("📊 Статистика"), KeyboardButton("📨 Рассылка")],
            [KeyboardButton("📋 Все заявки"), KeyboardButton("👥 Все пользователи")],
            [KeyboardButton("🗑️ Удалить заявку")]
        ]
        
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        # Проверяем, есть ли message (для callback-запросов может не быть)
        if update.message:
            logger.info("admin_panel: отправляем через update.message.reply_text")
            await update.message.reply_text(
                "🔧 **Панель администратора**\n\nВыберите действие:",
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            # Для callback-запросов отправляем новое сообщение
            logger.info(f"admin_panel: отправляем через context.bot.send_message в чат {update.effective_chat.id}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="🔧 **Панель администратора**\n\nВыберите действие:",
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def start_delete_application(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало удаления заявки"""
        user = update.effective_user
        
        if not self.is_admin(user.id):
            return
        
        # Получаем все заявки
        applications = self.db.get_applications()
        
        if not applications:
            await update.message.reply_text("❌ Заявок для удаления нет.")
            return
        
        # Показываем список заявок для удаления
        message = "🗑️ Выберите заявку для удаления:\n\n"
        
        for i, app in enumerate(applications[:10], 1):  # Показываем первые 10
            message += f"{i}. Заявка #{app['id']}\n"
            message += f"   👤 {app['name']}\n"
            message += f"   📞 {app['phone']}\n"
            message += f"   📅 {app['created_at']}\n\n"
        
        if len(applications) > 10:
            message += f"... и еще {len(applications) - 10} заявок\n\n"
        
        message += "Введите номер заявки для удаления:"
        
        # Сохраняем состояние для обработки номера заявки
        self.db.save_user_state(user.id, 'delete_application')
        
        await update.message.reply_text(message)
    
    async def view_applications(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Просмотр заявок"""
        user = update.effective_user
        
        if not self.is_admin(user.id):
            await update.message.reply_text("❌ У вас нет прав доступа к этой функции.")
            return
        
        try:
            applications = self.db.get_applications()
            
            if not applications:
                await update.message.reply_text("📋 Заявок пока нет.")
                # Возвращаемся в админ-меню
                await asyncio.sleep(2)
                await self.admin_panel(update, context)
                return
            
            # Отправляем общее сообщение о количестве заявок
            await update.message.reply_text(f"📋 **Все заявки ({len(applications)}):**\n")
            
            # Отправляем заявки по одной
            for i, app in enumerate(applications, 1):
                try:
                    await self.send_application_info(update, context, app)
                    # Увеличенная задержка между заявками для предотвращения таймаутов
                    if i < len(applications):
                        await asyncio.sleep(2)
                except Exception as e:
                    logger.error(f"Ошибка отправки заявки {app['id']}: {e}")
                    continue
            
            # Возвращаемся в админ-меню
            await asyncio.sleep(2)
            await self.admin_panel(update, context)
            
        except Exception as e:
            logger.error(f"Ошибка в view_applications: {e}")
            await update.message.reply_text("❌ Произошла ошибка при загрузке заявок.")
            # Возвращаемся в админ-меню
            await asyncio.sleep(2)
            await self.admin_panel(update, context)
    
    async def send_application_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE, app: dict):
        """Отправка информации о заявке БЕЗ кнопок"""
        try:
            # Получаем данные пользователя
            user_data = self.db.get_user_by_id(app['user_id'])
            
            # Экранируем данные для Markdown
            first_name = self.escape_markdown(user_data.get('first_name', 'Не указан'))
            username = self.escape_markdown(user_data.get('username', 'username'))
            name = self.escape_markdown(app['name'])
            phone = self.escape_markdown(app['phone'])
            additional_info = self.escape_markdown(app['additional_info'])
            
            # Формируем сообщение
            message = f"📧 **Заявка #{app['id']}**\n\n"
            message += f"👤 **Пользователь:** {first_name} (@{username})\n"
            message += f"🔥 **ФИО:** {name}\n"
            message += f"📞 **Телефон:** {phone}\n"
            message += f"💬 **Запрос:** {additional_info}\n"
            message += f"🕐 **Дата:** {app['created_at']}\n"
            status = app.get('status', 'Новая')
            status_emoji = "🆕" if status == 'Новая' else "✅" if status == 'Выполнена' else "❓"
            message += f"📊 **Статус:** {status_emoji} {status}"
            
            # Попытка отправки с обработкой таймаута
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=message,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    break  # Успешно отправлено
                except Exception as timeout_error:
                    if attempt < max_retries - 1:
                        logger.warning(f"Попытка {attempt + 1} неудачна, повторяем: {timeout_error}")
                        await asyncio.sleep(1)  # Ждем перед повтором
                    else:
                        raise timeout_error  # Последняя попытка неудачна
            
        except Exception as e:
            logger.error(f"Ошибка отправки информации о заявке {app.get('id', 'Unknown')}: {e}")
            # Отправляем упрощенное сообщение без Markdown
            try:
                simple_message = f"📧 Заявка #{app['id']}\n"
                simple_message += f"👤 Пользователь: {user_data.get('first_name', 'Не указан')}\n"
                simple_message += f"🔥 ФИО: {app['name']}\n"
                simple_message += f"📞 Телефон: {app['phone']}\n"
                simple_message += f"💬 Запрос: {app['additional_info']}\n"
                simple_message += f"🕐 Дата: {app['created_at']}\n"
                simple_message += f"📊 Статус: {app.get('status', 'Новая')}"
                
                # Попытка отправки простого сообщения с обработкой таймаута
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        await context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=simple_message
                        )
                        break  # Успешно отправлено
                    except Exception as timeout_error:
                        if attempt < max_retries - 1:
                            logger.warning(f"Попытка {attempt + 1} отправки простого сообщения неудачна: {timeout_error}")
                            await asyncio.sleep(1)  # Ждем перед повтором
                        else:
                            logger.error(f"Не удалось отправить простое сообщение после {max_retries} попыток: {timeout_error}")
            except Exception as e2:
                logger.error(f"Критическая ошибка отправки заявки: {e2}")
    
    async def send_application_card(self, update: Update, context: ContextTypes.DEFAULT_TYPE, app: dict, is_reply: bool = True):
        """Отправка карточки заявки с кнопками"""
        # Получаем данные пользователя
        user_data = self.db.get_user_by_id(app['user_id'])
        
        # Экранируем данные для Markdown
        first_name = self.escape_markdown(user_data.get('first_name', 'Не указан'))
        username = self.escape_markdown(user_data.get('username', 'username'))
        name = self.escape_markdown(app['name'])
        phone = self.escape_markdown(app['phone'])
        additional_info = self.escape_markdown(app['additional_info'])
        
        # Формируем сообщение в стиле скриншота
        message = f"📧 **Заявка #{app['id']}**\n\n"
        message += f"👤 **Пользователь:** {first_name} (@{username})\n"
        message += f"🔥 **ФИО:** {name}\n"
        message += f"📞 **Телефон:** {phone}\n"
        message += f"💬 **Запрос:** {additional_info}\n"
        message += f"🕐 **Дата:** {app['created_at']}\n"
        status = app.get('status', 'Новая')
        status_emoji = "🆕" if status == 'Новая' else "✅" if status == 'Выполнена' else "❓"
        message += f"📊 **Статус:** {status_emoji} {status}"
        
        # Создаем inline клавиатуру
        keyboard = [
            [
                InlineKeyboardButton("💬 Ответить", callback_data=f"reply_{app['id']}"),
                InlineKeyboardButton("✅ Завершить", callback_data=f"complete_{app['id']}")
            ],
            [
                InlineKeyboardButton("🗑️ Удалить", callback_data=f"delete_{app['id']}")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if is_reply:
            await update.message.reply_text(
                message,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def view_inactive_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Просмотр пользователей без заявок"""
        user = update.effective_user
        
        if not self.is_admin(user.id):
            return
        
        inactive_users = self.db.get_users_without_applications()
        
        if not inactive_users:
            await update.message.reply_text("Все пользователи оформили заявки! 🎉")
            return
        
        # Отправляем пользователей по 5 штук
        for i in range(0, len(inactive_users), 5):
            batch = inactive_users[i:i+5]
            message = "👥 **Пользователи без заявок:**\n\n"
            
            for user_data in batch:
                username = f"@{user_data['username']}" if user_data['username'] else "не указан"
                first_name = user_data['first_name'] or "Не указано"
                last_activity = user_data['last_seen'] or user_data['last_activity']
                
                # Используем функцию экранирования
                first_name = self.escape_markdown(first_name)
                username = self.escape_markdown(username)
                
                message += f"**ID:** {user_data['telegram_id']}\n"
                message += f"**Имя:** {first_name}\n"
                message += f"**Username:** {username}\n"
                message += f"**Последняя активность:** {last_activity}\n"
                message += "─" * 30 + "\n\n"
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        
        # Отправляем статистику
        total_users = len(self.db.get_all_users())
        users_with_apps = len(self.db.get_applications())
        inactive_count = len(inactive_users)
        
        stats_message = f"""
📊 **Статистика активности:**

👥 **Всего пользователей:** {total_users}
📋 **С заявками:** {users_with_apps}
❌ **Без заявок:** {inactive_count}
📈 **Конверсия:** {(users_with_apps/total_users*100):.1f}% (если есть пользователи)
        """
        
        await update.message.reply_text(stats_message, parse_mode=ParseMode.MARKDOWN)
    
    async def start_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало рассылки"""
        user = update.effective_user
        
        if not self.is_admin(user.id):
            return
        
        # Создаем клавиатуру с кнопкой отмены
        keyboard = [
            [InlineKeyboardButton("❌ Отменить рассылку", callback_data="cancel_broadcast")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        self.db.save_user_state(user.id, 'broadcast_message')
        await update.message.reply_text(
            "📢 **Рассылка**\n\nВведите сообщение для рассылки:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ статистики"""
        user = update.effective_user
        
        if not self.is_admin(user.id):
            return
        
        app_count = self.db.get_application_count()
        users = self.db.get_all_users()
        user_count = len(users)
        
        stats_message = f"""
📊 **Статистика бота:**

👥 **Пользователи:** {user_count}
📋 **Заявки:** {app_count}
📅 **Дата:** {datetime.now().strftime('%d.%m.%Y %H:%M')}
        """
        
        await update.message.reply_text(stats_message, parse_mode=ParseMode.MARKDOWN)
        
        # Возвращаемся в админ-меню через 3 секунды
        await asyncio.sleep(3)
        await self.admin_panel(update, context)
    
    async def notify_admin_new_application(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                         name: str, phone: str, additional_info: str, app_id: int = None):
        """Уведомление администраторов о новой заявке"""
        try:
            user = update.effective_user
            
            # Получаем ID заявки
            if app_id is not None:
                new_app_id = app_id
            else:
                # Fallback: получаем ID последней заявки
                applications = self.db.get_applications()
                if applications:
                    new_app_id = max(app['id'] for app in applications)
                else:
                    new_app_id = 1
            
            # Экранируем данные для Markdown
            first_name = self.escape_markdown(user.first_name or 'Не указан')
            username = self.escape_markdown(user.username or 'username')
            name_escaped = self.escape_markdown(name)
            phone_escaped = self.escape_markdown(phone)
            additional_info_escaped = self.escape_markdown(additional_info or 'не указано')
            
            message = f"🆕 **Новая заявка!**\n\n"
            message += f"📄 **Заявка #{new_app_id}**\n"
            message += f"👤 **Пользователь:** {first_name} (@{username})\n"
            message += f"🔥 **ФИО:** {name_escaped}\n"
            message += f"📞 **Телефон:** {phone_escaped}\n"
            message += f"💬 **Запрос:** {additional_info_escaped}\n"
            message += f"🕐 **Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            message += f"📊 **Статус:** 🆕 Новая"
            
            # Создаем inline клавиатуру
            keyboard = [
                [
                    InlineKeyboardButton("💬 Ответить", callback_data=f"reply_{new_app_id}"),
                    InlineKeyboardButton("✅ Завершить", callback_data=f"complete_{new_app_id}")
                ],
                [
                    InlineKeyboardButton("🗑️ Удалить", callback_data=f"delete_{new_app_id}")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Отправляем уведомление всем администраторам
            for admin_id in ADMIN_USER_IDS:
                try:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=message,
                        reply_markup=reply_markup,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    logger.info(f"Уведомление о заявке #{new_app_id} отправлено администратору {admin_id}")
                except Exception as e:
                    logger.error(f"Ошибка отправки уведомления о заявке #{new_app_id} администратору {admin_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Критическая ошибка в notify_admin_new_application: {e}")
    
    async def send_broadcast_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отправка сообщения рассылки"""
        user = update.effective_user
        text = update.message.text
        
        if not self.is_admin(user.id):
            return
        
        # Получаем всех пользователей
        users = self.db.get_all_users()
        
        if not users:
            await update.message.reply_text("Нет пользователей для рассылки.")
            return
        
        # Отправляем сообщение всем пользователям
        sent_count = 0
        failed_count = 0
        
        for user_data in users:
            try:
                await context.bot.send_message(
                    chat_id=user_data['telegram_id'],
                    text=text
                )
                sent_count += 1
            except Exception as e:
                logger.error(f"Ошибка отправки сообщения пользователю {user_data['telegram_id']}: {e}")
                failed_count += 1
        
        # Очищаем состояние
        self.db.clear_user_state(user.id)
        
        # Уведомляем администратора о результате
        result_message = f"""
📢 **Рассылка завершена!**

✅ **Отправлено:** {sent_count}
❌ **Ошибок:** {failed_count}
📊 **Всего пользователей:** {len(users)}
        """
        
        await update.message.reply_text(result_message)
    
    async def handle_cancel_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка отмены рассылки"""
        query = update.callback_query
        user = update.effective_user
        
        # Очищаем состояние
        self.db.clear_user_state(user.id)
        
        await query.edit_message_text("❌ Рассылка отменена")
        
        # Возвращаемся в админ-меню
        await asyncio.sleep(1)
        await self.admin_panel(update, context)
    
    def run(self):
        """Запуск бота"""
        if not BOT_TOKEN:
            logger.error("BOT_TOKEN не установлен!")
            return
        
        # Создаем приложение
        self.application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Запускаем бота
        logger.info("Запуск бота...")
        try:
            # Создаем новый event loop для этого потока
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.application.run_polling())
        except Exception as e:
            logger.error(f"Ошибка при запуске бота: {e}")

if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()
