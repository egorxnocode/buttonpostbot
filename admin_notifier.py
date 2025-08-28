"""
Модуль для отправки уведомлений администратору
"""
import logging
from typing import Dict, Any, Optional
import aiohttp
from config import ADMIN_BOT_TOKEN, ADMIN_CHAT_ID

logger = logging.getLogger(__name__)

class AdminNotifier:
    def __init__(self):
        """Инициализация уведомителя админа"""
        self.bot_token = ADMIN_BOT_TOKEN
        self.chat_id = ADMIN_CHAT_ID
        
        if not self.bot_token or not self.chat_id:
            logger.warning("ADMIN_BOT_TOKEN или ADMIN_CHAT_ID не установлены")
            
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    async def notify_timeout(self, user_data: Dict[str, Any], session_id: int) -> bool:
        """
        Уведомление админа о таймауте генерации поста
        
        Args:
            user_data (Dict): Данные пользователя
            session_id (int): ID сессии
            
        Returns:
            bool: True если уведомление отправлено успешно
        """
        if not self.bot_token or not self.chat_id:
            logger.error("Настройки админского бота не настроены")
            return False

        try:
            user_info = self._format_user_info(user_data)
            
            message = f"""
⚠️ **ТАЙМАУТ ГЕНЕРАЦИИ ПОСТА**

👤 Пользователь: {user_info}
🆔 Session ID: {session_id}
⏰ Превышен таймаут ожидания ответа от n8n (3 минуты)

📧 Email: {user_data.get('email', 'N/A')}
📺 Канал: {user_data.get('channel_url', 'N/A')}

Сессия будет сброшена, пользователь начнет процесс заново.
"""

            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': True
            }

            timeout = aiohttp.ClientTimeout(total=10)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self.api_url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"Уведомление о таймауте отправлено админу для сессии {session_id}")
                        return True
                    else:
                        logger.error(f"Ошибка при отправке уведомления админу: {response.status}")
                        return False

        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления админу: {e}")
            return False

    async def notify_error(self, error_message: str, user_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Уведомление админа об ошибке
        
        Args:
            error_message (str): Сообщение об ошибке
            user_data (Optional[Dict]): Данные пользователя (если есть)
            
        Returns:
            bool: True если уведомление отправлено успешно
        """
        if not self.bot_token or not self.chat_id:
            return False

        try:
            message = f"🚨 **ОШИБКА В БОТЕ**\n\n{error_message}"
            
            if user_data:
                user_info = self._format_user_info(user_data)
                message += f"\n\n👤 Пользователь: {user_info}"

            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': True
            }

            timeout = aiohttp.ClientTimeout(total=10)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self.api_url, json=payload) as response:
                    if response.status == 200:
                        logger.info("Уведомление об ошибке отправлено админу")
                        return True
                    else:
                        logger.error(f"Ошибка при отправке уведомления об ошибке: {response.status}")
                        return False

        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления об ошибке: {e}")
            return False

    async def notify_stats(self, stats: Dict[str, Any]) -> bool:
        """
        Отправка статистики админу
        
        Args:
            stats (Dict): Статистика использования
            
        Returns:
            bool: True если уведомление отправлено успешно
        """
        if not self.bot_token or not self.chat_id:
            return False

        try:
            message = f"""
📊 **СТАТИСТИКА БОТА**

👥 Всего пользователей: {stats.get('total_users', 0)}
✅ Зарегистрированных: {stats.get('registered_users', 0)}
📝 Активных сессий: {stats.get('active_sessions', 0)}
🎯 Постов создано сегодня: {stats.get('posts_today', 0)}
"""

            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': True
            }

            timeout = aiohttp.ClientTimeout(total=10)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self.api_url, json=payload) as response:
                    return response.status == 200

        except Exception as e:
            logger.error(f"Ошибка при отправке статистики: {e}")
            return False

    def _format_user_info(self, user_data: Dict[str, Any]) -> str:
        """
        Форматирование информации о пользователе
        
        Args:
            user_data (Dict): Данные пользователя
            
        Returns:
            str: Отформатированная информация
        """
        name_parts = []
        
        if user_data.get('first_name'):
            name_parts.append(user_data['first_name'])
        if user_data.get('last_name'):
            name_parts.append(user_data['last_name'])
        
        name = ' '.join(name_parts) if name_parts else 'Без имени'
        username = f"@{user_data.get('username')}" if user_data.get('username') else 'Без username'
        telegram_id = user_data.get('telegram_id', 'N/A')
        
        return f"{name} ({username}) [ID: {telegram_id}]"
