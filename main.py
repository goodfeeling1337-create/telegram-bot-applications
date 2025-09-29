import asyncio
import logging
import signal
import sys
from concurrent.futures import ThreadPoolExecutor

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
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    def start(self):
        """Запуск бота и системы напоминаний"""
        try:
            logger.info("Запуск Telegram бота...")
            
            # Запускаем бота в отдельном потоке
            self.executor.submit(self.bot.run)
            
            # Запускаем систему напоминаний в отдельном потоке
            self.executor.submit(self._run_reminder_system)
            
            logger.info("Бот успешно запущен!")
            
        except Exception as e:
            logger.error(f"Ошибка при запуске бота: {e}")
    
    def _run_reminder_system(self):
        """Запуск системы напоминаний в отдельном потоке"""
        try:
            asyncio.run(start_reminder_system())
        except Exception as e:
            logger.error(f"Ошибка в системе напоминаний: {e}")
    
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
            
            # Закрываем executor
            self.executor.shutdown(wait=True)
            
            logger.info("Бот остановлен")
            
        except Exception as e:
            logger.error(f"Ошибка при остановке бота: {e}")

def signal_handler(signum, frame):
    """Обработчик сигналов для корректного завершения"""
    logger.info(f"Получен сигнал {signum}, завершение работы...")
    sys.exit(0)

def main():
    """Главная функция"""
    # Настраиваем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Создаем и запускаем менеджер бота
    bot_manager = BotManager()
    
    try:
        bot_manager.start()
        
        # Ждем бесконечно, пока бот работает
        while True:
            import time
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        # Останавливаем бота синхронно
        try:
            if bot_manager.bot.application:
                bot_manager.bot.application.updater.stop()
                bot_manager.bot.application.stop()
        except Exception as e:
            logger.error(f"Ошибка при остановке бота: {e}")
        
        # Закрываем executor
        bot_manager.executor.shutdown(wait=True)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Программа завершена пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)
