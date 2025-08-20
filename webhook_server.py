"""
Простой веб-сервер для обработки webhook от n8n
"""
import logging
import asyncio
from aiohttp import web, ClientError
import json
from webhook_handler import process_n8n_webhook

logger = logging.getLogger(__name__)

async def handle_n8n_webhook(request):
    """Обработчик webhook от n8n"""
    try:
        # Получаем JSON данные
        data = await request.json()
        logger.info(f"Получен webhook от n8n: {data}")
        
        # Обрабатываем webhook
        response = await process_n8n_webhook(data)
        
        return web.json_response(response)
        
    except json.JSONDecodeError:
        logger.error("Некорректный JSON в webhook от n8n")
        return web.json_response(
            {"status": "error", "message": "Invalid JSON"},
            status=400
        )
    except Exception as e:
        logger.error(f"Ошибка при обработке webhook от n8n: {e}")
        return web.json_response(
            {"status": "error", "message": str(e)},
            status=500
        )

async def health_check(request):
    """Проверка здоровья сервера"""
    return web.json_response({"status": "ok", "service": "telegram-bot-webhook"})

def create_app():
    """Создание приложения aiohttp"""
    app = web.Application()
    
    # Добавляем маршруты
    app.router.add_post('/webhook/n8n', handle_n8n_webhook)
    app.router.add_get('/health', health_check)
    
    return app

async def run_webhook_server(host='0.0.0.0', port=8080):
    """Запуск веб-сервера для webhook"""
    app = create_app()
    
    logger.info(f"Запуск webhook сервера на {host}:{port}")
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, host, port)
    await site.start()
    
    logger.info(f"Webhook сервер запущен на http://{host}:{port}")
    
    # Возвращаем runner для возможности остановки
    return runner

if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    async def main():
        runner = await run_webhook_server()
        
        try:
            # Держим сервер запущенным
            while True:
                await asyncio.sleep(3600)  # Спим час
        except KeyboardInterrupt:
            logger.info("Остановка webhook сервера...")
        finally:
            await runner.cleanup()
    
    asyncio.run(main())
