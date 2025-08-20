"""
Главный файл для запуска Telegram бота и webhook сервера
"""
import asyncio
import logging
import signal
import sys
from bot import TelegramBot
from webhook_server import run_webhook_server

logger = logging.getLogger(__name__)

class BotApplication:
    def __init__(self):
        """Инициализация приложения"""
        self.bot = None
        self.webhook_runner = None
        self.running = True

    async def start(self):
        """Запуск бота"""
        try:
            logger.info("Запуск приложения...")
            
            # Создаем и запускаем только бота (БЕЗ webhook сервера)
            logger.info("Инициализация Telegram бота...")
            self.bot = TelegramBot()
            
            logger.info("Запуск Telegram бота...")
            logger.info("Приложение запущено успешно")
            logger.info("Telegram бот: активен")
            
            # Запускаем бота напрямую (синхронно)
            self.bot.run()
                    
        except Exception as e:
            logger.error(f"Ошибка при запуске приложения: {e}")
            raise
    
    async def _run_webhook_server(self):
        """Запуск webhook сервера"""
        self.webhook_runner = await run_webhook_server(port=8080)
        
        # Ждем бесконечно, пока сервер работает
        try:
            while self.running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("Webhook сервер получил сигнал остановки")
            raise
    
    async def _run_bot(self):
        """Запуск Telegram бота"""
        try:
            # Используем синхронный метод в отдельном потоке
            import asyncio
            import concurrent.futures
            
            def run_bot_sync():
                self.bot.application.run_polling(drop_pending_updates=True)
            
            # Запускаем в отдельном thread pool
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                await loop.run_in_executor(executor, run_bot_sync)
                
        except Exception as e:
            logger.error(f"Ошибка в Telegram боте: {e}")
            raise

    async def stop(self):
        """Остановка приложения"""
        logger.info("Остановка приложения...")
        
        self.running = False
        
        # Останавливаем веб-сервер
        if self.webhook_runner:
            await self.webhook_runner.cleanup()
            logger.info("Webhook сервер остановлен")
        
        # Бот остановится автоматически при завершении процесса
        logger.info("Приложение остановлено")

def setup_signal_handlers(app):
    """Настройка обработчиков сигналов"""
    
    def signal_handler(signum, frame):
        logger.info(f"Получен сигнал {signum}")
        asyncio.create_task(app.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def main():
    """Главная функция"""
    # Настройка логирования
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    app = BotApplication()
    
    try:
        # Запускаем синхронно
        asyncio.run(app.start())
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки от пользователя")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Приложение остановлено пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске: {e}")
        sys.exit(1)
