"""
Обработчик webhook от n8n для получения сгенерированных постов
"""
import logging
import re
from typing import Dict, Any, Optional
from telegram import Bot
from database import Database
from config import TELEGRAM_BOT_TOKEN, MESSAGES

logger = logging.getLogger(__name__)

class WebhookHandler:
    def __init__(self):
        """Инициализация обработчика webhook"""
        self.db = Database()
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)

    async def handle_n8n_response(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Обработка ответа от n8n с сгенерированным постом
        
        Args:
            data (Dict): Данные от n8n
            
        Returns:
            Dict: Ответ для n8n
        """
        try:
            # Извлекаем данные из запроса
            telegram_id = data.get('telegram_id')
            generated_post = data.get('generated_post')
            
            if not telegram_id or not generated_post:
                logger.error(f"Неполные данные от n8n: {data}")
                return {"status": "error", "message": "Missing required fields"}
            
            # Очищаем HTML от неподдерживаемых тегов
            cleaned_post = self._clean_html_for_telegram(generated_post)
            
            # Находим активную сессию пользователя
            session = await self.db.get_active_post_session(telegram_id)
            
            if not session or session['session_status'] != 'generating':
                logger.error(f"Активная сессия не найдена для пользователя {telegram_id}")
                return {"status": "error", "message": "Active session not found"}
            
            # Обновляем сессию с очищенным постом
            success = await self.db.update_session_status(
                session['id'], 
                'reviewing', 
                cleaned_post
            )
            
            if not success:
                logger.error(f"Ошибка при обновлении сессии {session['id']}")
                return {"status": "error", "message": "Failed to update session"}
            
            # Отправляем очищенный пост на проверку пользователю
            await self._send_post_for_review(telegram_id, cleaned_post)
            
            logger.info(f"Пост успешно отправлен на проверку пользователю {telegram_id}")
            return {"status": "success", "message": "Post sent for review"}
            
        except Exception as e:
            logger.error(f"Ошибка при обработке ответа от n8n: {e}")
            return {"status": "error", "message": str(e)}

    async def _send_post_for_review(self, telegram_id: int, generated_post: str):
        """
        Отправка сгенерированного поста пользователю на проверку
        
        Args:
            telegram_id (int): Telegram ID пользователя
            generated_post (str): Сгенерированный пост
        """
        try:
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            
            # Создаем клавиатуру для проверки
            keyboard = [
                [
                    InlineKeyboardButton("✅ Верно", callback_data="post_approved"),
                    InlineKeyboardButton("❌ Нет", callback_data="post_rejected")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Форматируем сообщение с постом
            review_message = MESSAGES['post_review'].format(post_content=generated_post)
            
            # Отправляем пост на проверку
            await self.bot.send_message(
                chat_id=telegram_id,
                text=review_message,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка при отправке поста на проверку пользователю {telegram_id}: {e}")
            raise

    def _clean_html_for_telegram(self, html_text: str) -> str:
        """
        Очистка HTML от неподдерживаемых Telegram тегов
        
        Args:
            html_text (str): HTML текст от N8N
            
        Returns:
            str: Очищенный текст с поддерживаемыми тегами
        """
        try:
            # Заменяем неподдерживаемые теги на поддерживаемые или убираем их
            
            # <p> заменяем на двойной перенос строки
            html_text = re.sub(r'<p[^>]*>', '', html_text)
            html_text = re.sub(r'</p>', '\n\n', html_text)
            
            # <br> и <br/> заменяем на \n
            html_text = re.sub(r'<br\s*/?>', '\n', html_text)
            
            # <div> убираем, оставляем содержимое
            html_text = re.sub(r'<div[^>]*>', '', html_text)
            html_text = re.sub(r'</div>', '\n', html_text)
            
            # <span> убираем, оставляем содержимое  
            html_text = re.sub(r'<span[^>]*>', '', html_text)
            html_text = re.sub(r'</span>', '', html_text)
            
            # <h1>, <h2>, <h3> заменяем на жирный текст
            html_text = re.sub(r'<h[1-6][^>]*>', '<b>', html_text)
            html_text = re.sub(r'</h[1-6]>', '</b>\n\n', html_text)
            
            # Убираем остальные неподдерживаемые теги (сохраняем содержимое)
            unsupported_tags = ['ul', 'ol', 'li', 'table', 'tr', 'td', 'th', 'thead', 'tbody']
            for tag in unsupported_tags:
                html_text = re.sub(f'<{tag}[^>]*>', '', html_text)
                html_text = re.sub(f'</{tag}>', '\n', html_text)
            
            # Убираем множественные переносы строк
            html_text = re.sub(r'\n{3,}', '\n\n', html_text)
            
            # Убираем пробелы в начале и конце
            html_text = html_text.strip()
            
            logger.info(f"HTML очищен от неподдерживаемых тегов")
            return html_text
            
        except Exception as e:
            logger.error(f"Ошибка при очистке HTML: {e}")
            # В случае ошибки возвращаем исходный текст
            return html_text

# Функция для использования в веб-сервере (например, FastAPI или Flask)
async def process_n8n_webhook(request_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Функция для обработки webhook от n8n
    
    Args:
        request_data (Dict): Данные от n8n
        
    Returns:
        Dict: Ответ для n8n
    """
    handler = WebhookHandler()
    return await handler.handle_n8n_response(request_data)
