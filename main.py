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
            
            # Создаем задачи для параллельного выполнения
            tasks = []
            
            # Запускаем веб-сервер для webhook
            logger.info("Запуск webhook сервера...")
            webhook_task = asyncio.create_task(self._run_webhook_server())
            tasks.append(webhook_task)
            
            # Создаем и запускаем бота
            logger.info("Инициализация Telegram бота...")
            self.bot = TelegramBot()
            
            # Запускаем бота в отдельной задаче
            logger.info("Запуск Telegram бота...")
            bot_task = asyncio.create_task(self._run_bot())
            tasks.append(bot_task)
            
            logger.info("Приложение запущено успешно")
            logger.info("Webhook сервер: http://0.0.0.0:8080")
            logger.info("Telegram бот: активен")
            
            # Ждем завершения любой задачи (обычно по ошибке)
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            
            # Отменяем оставшиеся задачи
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            # Проверяем, была ли ошибка в завершившейся задаче
            for task in done:
                if task.exception():
                    raise task.exception()
                    
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
