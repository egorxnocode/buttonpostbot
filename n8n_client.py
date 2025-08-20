"""
Модуль для интеграции с n8n через webhook
"""
import logging
import asyncio
from typing import Optional, Dict, Any
import aiohttp
from config import N8N_WEBHOOK_URL

logger = logging.getLogger(__name__)

class N8NClient:
    def __init__(self):
        """Инициализация клиента n8n"""
        self.webhook_url = N8N_WEBHOOK_URL
        if not self.webhook_url:
            logger.warning("N8N_WEBHOOK_URL не установлен")

    async def send_post_generation_request(self, user_data: Dict[str, Any], 
                                         answers: Dict[str, str]) -> bool:
        """
        Отправка запроса на генерацию поста в n8n
        
        Args:
            user_data (Dict): Данные пользователя
            answers (Dict): Ответы на вопросы
            
        Returns:
            bool: True если запрос отправлен успешно
        """
        if not self.webhook_url:
            logger.error("N8N_WEBHOOK_URL не настроен")
            return False

        try:
            payload = {
                "user": {
                    "telegram_id": user_data.get('telegram_id'),
                    "email": user_data.get('email'),
                    "channel_url": user_data.get('channel_url'),
                    "first_name": user_data.get('first_name'),
                    "last_name": user_data.get('last_name')
                },
                "answers": {
                    "topic": answers.get('answer_1'),
                    "goal": answers.get('answer_2'), 
                    "additional_info": answers.get('answer_3')
                },
                "request_type": "generate_post",
                "timestamp": asyncio.get_event_loop().time()
            }

            timeout = aiohttp.ClientTimeout(total=10)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    
                    if response.status == 200:
                        logger.info(f"Запрос на генерацию поста отправлен успешно для пользователя {user_data.get('telegram_id')}")
                        return True
                    else:
                        logger.error(f"Ошибка при отправке запроса в n8n: {response.status}")
                        return False

        except asyncio.TimeoutError:
            logger.error("Таймаут при отправке запроса в n8n")
            return False
        except Exception as e:
            logger.error(f"Ошибка при отправке запроса в n8n: {e}")
            return False

    async def notify_timeout(self, user_data: Dict[str, Any], session_id: int) -> bool:
        """
        Уведомление n8n о таймауте генерации
        
        Args:
            user_data (Dict): Данные пользователя
            session_id (int): ID сессии
            
        Returns:
            bool: True если уведомление отправлено успешно
        """
        if not self.webhook_url:
            return False

        try:
            payload = {
                "user": {
                    "telegram_id": user_data.get('telegram_id'),
                    "email": user_data.get('email')
                },
                "session_id": session_id,
                "request_type": "timeout_notification",
                "timestamp": asyncio.get_event_loop().time()
            }

            timeout = aiohttp.ClientTimeout(total=5)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    
                    logger.info(f"Уведомление о таймауте отправлено для пользователя {user_data.get('telegram_id')}")
                    return response.status == 200

        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления о таймауте: {e}")
            return False
