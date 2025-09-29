import asyncio
import logging
from datetime import datetime, timedelta
from telegram import Bot
from config import BOT_TOKEN, MESSAGES, ADMIN_USER_IDS
from database import Database

logger = logging.getLogger(__name__)

class ReminderSystem:
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN) if BOT_TOKEN else None
        self.db = Database()
        self.running = False
    
    async def send_reminders(self):
        """Отправка напоминаний пользователям с незавершенными заявками"""
        if not self.bot:
            logger.error("Бот не инициализирован для отправки напоминаний")
            return
        
        try:
            # Получаем пользователей с незавершенными заявками
            incomplete_applications = self.db.get_incomplete_applications()
            
            for app in incomplete_applications:
                try:
                    # Отправляем напоминание
                    await self.bot.send_message(
                        chat_id=app['user_id'],
                        text=MESSAGES['reminder']
                    )
                    
                    # Обновляем время последней активности
                    self.db.save_user_state(
                        app['user_id'], 
                        app['state'], 
                        app['data']
                    )
                    
                    logger.info(f"Напоминание отправлено пользователю {app['user_id']}")
                    
                except Exception as e:
                    logger.error(f"Ошибка отправки напоминания пользователю {app['user_id']}: {e}")
            
            if incomplete_applications:
                logger.info(f"Отправлено {len(incomplete_applications)} напоминаний")
                
        except Exception as e:
            logger.error(f"Ошибка в системе напоминаний: {e}")
    
    async def run_reminder_loop(self):
        """Запуск цикла проверки напоминаний"""
        self.running = True
        logger.info("Система напоминаний запущена")
        
        while self.running:
            try:
                await self.send_reminders()
                # Проверяем каждые 6 часов
                await asyncio.sleep(6 * 60 * 60)
            except Exception as e:
                logger.error(f"Ошибка в цикле напоминаний: {e}")
                await asyncio.sleep(60)  # Ждем минуту перед повтором
    
    def stop(self):
        """Остановка системы напоминаний"""
        self.running = False
        logger.info("Система напоминаний остановлена")

# Функция для запуска системы напоминаний в отдельном потоке
async def start_reminder_system():
    """Запуск системы напоминаний"""
    reminder_system = ReminderSystem()
    await reminder_system.run_reminder_loop()

if __name__ == "__main__":
    # Для тестирования системы напоминаний
    asyncio.run(start_reminder_system())
