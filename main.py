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
        """Запуск бота и веб-сервера"""
        try:
            logger.info("Запуск приложения...")
            
            # Запускаем веб-сервер для webhook
            self.webhook_runner = await run_webhook_server(port=8080)
            
            # Создаем и запускаем бота
            self.bot = TelegramBot()
            
            # Запускаем бота асинхронно
            await self.bot.run()
            
            logger.info("Приложение запущено успешно")
            logger.info("Webhook сервер: http://0.0.0.0:8080")
            logger.info("Telegram бот: активен")
            
        except Exception as e:
            logger.error(f"Ошибка при запуске приложения: {e}")
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

async def main():
    """Главная функция"""
    # Настройка логирования
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    app = BotApplication()
    setup_signal_handlers(app)
    
    try:
        await app.start()
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки от пользователя")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)
    finally:
        await app.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Приложение остановлено пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске: {e}")
        sys.exit(1)
