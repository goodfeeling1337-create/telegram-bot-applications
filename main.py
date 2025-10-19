import asyncio
import logging
import signal
import sys

from bot import TelegramBot
from reminder_system import start_reminder_system

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class BotManager:
    def __init__(self):
        self.bot = TelegramBot()
        self.reminder_task = None
    
    async def start(self):
        """Запуск бота и системы напоминаний"""
        try:
            logger.info("Запуск Telegram бота...")
            
            # Запускаем систему напоминаний как задачу
            self.reminder_task = asyncio.create_task(start_reminder_system())
            
            # Запускаем бота
            await self.bot.run_async()
            
            logger.info("Бот успешно запущен!")
            
        except Exception as e:
            logger.error(f"Ошибка при запуске бота: {e}")
            raise
    
    async def stop(self):
        """Остановка бота и системы напоминаний"""
        try:
            logger.info("Остановка бота...")
            
            # Останавливаем систему напоминаний
            if self.reminder_task:
                self.reminder_task.cancel()
                try:
                    await self.reminder_task
                except asyncio.CancelledError:
                    pass
            
            # Останавливаем бота
            if self.bot.application:
                await self.bot.application.updater.stop()
                await self.bot.application.stop()
                await self.bot.application.shutdown()
            
            logger.info("Бот остановлен")
            
        except Exception as e:
            logger.error(f"Ошибка при остановке бота: {e}")

def signal_handler(signum, frame):
    """Обработчик сигналов для корректного завершения"""
    logger.info(f"Получен сигнал {signum}, завершение работы...")
    sys.exit(0)

async def main():
    """Главная функция"""
    # Настраиваем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Создаем и запускаем менеджер бота
    bot_manager = BotManager()
    
    try:
        await bot_manager.start()
        
    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        await bot_manager.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Программа завершена пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)