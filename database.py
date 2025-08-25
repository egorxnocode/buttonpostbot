"""
Модуль для работы с базой данных Supabase
"""
import logging
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY, REGISTRATION_STEPS

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        """Инициализация подключения к Supabase"""
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL и SUPABASE_KEY должны быть установлены")
        
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Подключение к Supabase установлено")

    async def find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Поиск пользователя по email
        
        Args:
            email (str): Email адрес в нижнем регистре
            
        Returns:
            Optional[Dict]: Данные пользователя или None если не найден
        """
        try:
            result = self.supabase.table('button_users').select('*').eq('email', email.lower()).execute()
            
            if result.data:
                logger.info(f"Пользователь найден по email: {email}")
                return result.data[0]
            else:
                logger.info(f"Пользователь не найден по email: {email}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка при поиске пользователя по email {email}: {e}")
            raise

    async def update_user_telegram_data(self, email: str, telegram_data: Dict[str, Any]) -> bool:
        """
        Обновление Telegram данных пользователя
        
        Args:
            email (str): Email пользователя
            telegram_data (Dict): Данные из Telegram
            
        Returns:
            bool: True если обновление успешно
        """
        try:
            update_data = {
                'telegram_id': telegram_data.get('telegram_id'),
                'username': telegram_data.get('username'),
                'first_name': telegram_data.get('first_name'),
                'last_name': telegram_data.get('last_name'),
                'registration_step': REGISTRATION_STEPS['EMAIL_CONFIRMED'],
                'last_activity': 'now()'
            }
            
            result = self.supabase.table('button_users').update(update_data).eq('email', email.lower()).execute()
            
            if result.data:
                logger.info(f"Telegram данные обновлены для пользователя: {email}")
                return True
            else:
                logger.error(f"Не удалось обновить данные для пользователя: {email}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка при обновлении Telegram данных для {email}: {e}")
            raise

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """
        Получение пользователя по Telegram ID
        
        Args:
            telegram_id (int): Telegram ID пользователя
            
        Returns:
            Optional[Dict]: Данные пользователя или None
        """
        try:
            result = self.supabase.table('button_users').select('*').eq('telegram_id', telegram_id).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при получении пользователя по telegram_id {telegram_id}: {e}")
            raise

    async def update_user_step(self, telegram_id: int, step: int) -> bool:
        """
        Обновление этапа регистрации пользователя
        
        Args:
            telegram_id (int): Telegram ID пользователя
            step (int): Новый этап регистрации
            
        Returns:
            bool: True если обновление успешно
        """
        try:
            result = self.supabase.table('button_users').update({
                'registration_step': step,
                'last_activity': 'now()'
            }).eq('telegram_id', telegram_id).execute()
            
            if result.data:
                logger.info(f"Этап регистрации обновлен для пользователя {telegram_id}: {step}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении этапа для пользователя {telegram_id}: {e}")
            raise

    async def update_channel_data(self, telegram_id: int, channel_url: str, 
                                channel_id: Optional[int] = None, 
                                channel_title: Optional[str] = None) -> bool:
        """
        Обновление данных канала пользователя
        
        Args:
            telegram_id (int): Telegram ID пользователя
            channel_url (str): URL канала
            channel_id (Optional[int]): ID канала
            channel_title (Optional[str]): Название канала
            
        Returns:
            bool: True если обновление успешно
        """
        try:
            update_data = {
                'channel_url': channel_url,
                'registration_step': REGISTRATION_STEPS['CHANNEL_ADDED'],
                'last_activity': 'now()'
            }
            
            if channel_id:
                update_data['channel_id'] = channel_id
            if channel_title:
                update_data['channel_title'] = channel_title
                
            result = self.supabase.table('button_users').update(update_data).eq('telegram_id', telegram_id).execute()
            
            if result.data:
                logger.info(f"Данные канала обновлены для пользователя {telegram_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении данных канала для пользователя {telegram_id}: {e}")
            raise

    async def update_admin_status(self, telegram_id: int, is_admin: bool) -> bool:
        """
        Обновление статуса администратора бота в канале
        
        Args:
            telegram_id (int): Telegram ID пользователя
            is_admin (bool): Статус администратора
            
        Returns:
            bool: True если обновление успешно
        """
        try:
            update_data = {
                'is_bot_admin': is_admin,
                'last_activity': 'now()'
            }
            
            if is_admin:
                update_data['registration_step'] = REGISTRATION_STEPS['COMPLETED']
                
            result = self.supabase.table('button_users').update(update_data).eq('telegram_id', telegram_id).execute()
            
            if result.data:
                logger.info(f"Статус администратора обновлен для пользователя {telegram_id}: {is_admin}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении статуса администратора для пользователя {telegram_id}: {e}")
            raise

    async def update_last_activity(self, telegram_id: int) -> bool:
        """
        Обновление времени последней активности пользователя
        
        Args:
            telegram_id (int): Telegram ID пользователя
            
        Returns:
            bool: True если обновление успешно
        """
        try:
            result = self.supabase.table('button_users').update({
                'last_activity': 'now()'
            }).eq('telegram_id', telegram_id).execute()
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении времени активности для пользователя {telegram_id}: {e}")
            return False

    # Методы для работы с сессиями создания постов
    
    async def create_post_session(self, user_id: int, telegram_id: int) -> Optional[int]:
        """
        Создание новой сессии создания поста
        
        Args:
            user_id (int): ID пользователя в таблице button_users
            telegram_id (int): Telegram ID пользователя
            
        Returns:
            Optional[int]: ID созданной сессии или None при ошибке
        """
        try:
            # Сначала завершаем все активные сессии пользователя
            await self.cancel_active_sessions(telegram_id)
            
            result = self.supabase.table('button_post_creation_sessions').insert({
                'user_id': user_id,
                'telegram_id': telegram_id,
                'session_status': 'question_1'
            }).execute()
            
            if result.data:
                session_id = result.data[0]['id']
                logger.info(f"Создана новая сессия создания поста {session_id} для пользователя {telegram_id}")
                return session_id
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при создании сессии поста для пользователя {telegram_id}: {e}")
            return None

    async def get_active_post_session(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """
        Получение активной сессии создания поста
        
        Args:
            telegram_id (int): Telegram ID пользователя
            
        Returns:
            Optional[Dict]: Данные активной сессии или None
        """
        try:
            result = self.supabase.table('button_post_creation_sessions').select('*').eq(
                'telegram_id', telegram_id
            ).in_(
                'session_status', 
                ['started', 'question_1', 'question_2', 'question_3', 'generating', 'reviewing', 
                 'button_type_selection', 'button_config', 'button_text_selection', 'final_review']
            ).order('created_at', desc=True).limit(1).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при получении активной сессии для пользователя {telegram_id}: {e}")
            return None

    async def update_session_answer(self, session_id: int, answer_number: int, answer: str) -> bool:
        """
        Обновление ответа на вопрос в сессии
        
        Args:
            session_id (int): ID сессии
            answer_number (int): Номер вопроса (1, 2, 3, 4, 5, 6)
            answer (str): Ответ пользователя
            
        Returns:
            bool: True если обновление успешно
        """
        try:
            update_data = {f'answer_{answer_number}': answer}
            
            # Определяем следующий статус
            if answer_number == 1:
                update_data['session_status'] = 'question_2'
            elif answer_number == 2:
                update_data['session_status'] = 'question_3'
            elif answer_number == 3:
                update_data['session_status'] = 'question_4'
            elif answer_number == 4:
                update_data['session_status'] = 'question_5'
            elif answer_number == 5:
                update_data['session_status'] = 'question_6'
            elif answer_number == 6:
                update_data['session_status'] = 'collecting_links'
            
            result = self.supabase.table('button_post_creation_sessions').update(
                update_data
            ).eq('id', session_id).execute()
            
            if result.data:
                logger.info(f"Обновлен ответ {answer_number} в сессии {session_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении ответа {answer_number} в сессии {session_id}: {e}")
            return False

    async def update_session_status(self, session_id: int, status: str, 
                                  generated_post: Optional[str] = None) -> bool:
        """
        Обновление статуса сессии
        
        Args:
            session_id (int): ID сессии
            status (str): Новый статус
            generated_post (Optional[str]): Сгенерированный пост (если есть)
            
        Returns:
            bool: True если обновление успешно
        """
        try:
            update_data = {'session_status': status}
            
            if generated_post:
                update_data['generated_post'] = generated_post
            
            result = self.supabase.table('button_post_creation_sessions').update(
                update_data
            ).eq('id', session_id).execute()
            
            if result.data:
                logger.info(f"Обновлен статус сессии {session_id}: {status}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении статуса сессии {session_id}: {e}")
            return False

    async def cancel_active_sessions(self, telegram_id: int) -> bool:
        """
        Отмена всех активных сессий пользователя
        
        Args:
            telegram_id (int): Telegram ID пользователя
            
        Returns:
            bool: True если операция успешна
        """
        try:
            result = self.supabase.table('button_post_creation_sessions').update({
                'session_status': 'cancelled'
            }).eq('telegram_id', telegram_id).in_(
                'session_status', 
                ['started', 'question_1', 'question_2', 'question_3', 'generating', 'reviewing']
            ).execute()
            
            logger.info(f"Отменены активные сессии для пользователя {telegram_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при отмене активных сессий для пользователя {telegram_id}: {e}")
            return False

    async def get_session_answers(self, session_id: int) -> Optional[Dict[str, str]]:
        """
        Получение всех ответов из сессии
        
        Args:
            session_id (int): ID сессии
            
        Returns:
            Optional[Dict]: Словарь с ответами или None
        """
        try:
            result = self.supabase.table('button_post_creation_sessions').select(
                'answer_1, answer_2, answer_3, answer_4, answer_5, answer_6'
            ).eq('id', session_id).execute()
            
            if result.data:
                data = result.data[0]
                return {
                    'answer_1': data.get('answer_1'),
                    'answer_2': data.get('answer_2'),
                    'answer_3': data.get('answer_3'),
                    'answer_4': data.get('answer_4'),
                    'answer_5': data.get('answer_5'),
                    'answer_6': data.get('answer_6')
                }
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при получении ответов из сессии {session_id}: {e}")
            return None

    async def clear_session_answers(self, session_id: int) -> bool:
        """
        Очистка ответов в сессии (для перезапуска процесса)
        
        Args:
            session_id (int): ID сессии
            
        Returns:
            bool: True если очистка успешна
        """
        try:
            result = self.supabase.table('button_post_creation_sessions').update({
                'answer_1': None,
                'answer_2': None,
                'answer_3': None,
                'answer_4': None,
                'answer_5': None,
                'answer_6': None,
                'link_1': None,
                'link_2': None,
                'link_3': None,
                'link_4': None,
                'link_5': None,
                'generated_post': None,
                'session_status': 'question_1',
                'n8n_webhook_sent_at': None
            }).eq('id', session_id).execute()
            
            if result.data:
                logger.info(f"Очищены ответы в сессии {session_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка при очистке ответов в сессии {session_id}: {e}")
            return False

    async def get_session_links(self, session_id: int) -> Optional[Dict[str, str]]:
        """
        Получение ссылок из сессии
        
        Args:
            session_id (int): ID сессии
            
        Returns:
            Optional[Dict]: Словарь со ссылками или None
        """
        try:
            result = self.supabase.table('button_post_creation_sessions').select(
                'link_1, link_2, link_3, link_4, link_5'
            ).eq('id', session_id).execute()
            
            if result.data:
                data = result.data[0]
                return {
                    'link_1': data.get('link_1'),
                    'link_2': data.get('link_2'),
                    'link_3': data.get('link_3'),
                    'link_4': data.get('link_4'),
                    'link_5': data.get('link_5')
                }
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при получении ссылок из сессии {session_id}: {e}")
            return None

    async def update_session_link(self, session_id: int, link_number: int, link_url: str) -> bool:
        """
        Обновление ссылки в сессии
        
        Args:
            session_id (int): ID сессии
            link_number (int): Номер ссылки (1-5)
            link_url (str): URL ссылки
            
        Returns:
            bool: True если обновление успешно
        """
        try:
            if link_number < 1 or link_number > 5:
                logger.error(f"Неверный номер ссылки: {link_number}")
                return False
            
            update_data = {f'link_{link_number}': link_url}
            
            result = self.supabase.table('button_post_creation_sessions').update(
                update_data
            ).eq('id', session_id).execute()
            
            if result.data:
                logger.info(f"Обновлена ссылка {link_number} в сессии {session_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении ссылки {link_number} в сессии {session_id}: {e}")
            return False

    async def get_expired_generating_sessions(self, timeout_minutes: int = 3) -> List[Dict[str, Any]]:
        """
        Получение сессий, которые находятся в статусе generating дольше указанного времени
        
        Args:
            timeout_minutes (int): Таймаут в минутах
            
        Returns:
            List[Dict]: Список просроченных сессий
        """
        try:
            # Вычисляем время таймаута
            timeout_time = f"NOW() - INTERVAL '{timeout_minutes} minutes'"
            
            result = self.supabase.table('button_post_creation_sessions').select('*').eq(
                'session_status', 'generating'
            ).filter(
                'n8n_webhook_sent_at', 'lt', f'now() - interval \'{timeout_minutes} minutes\''
            ).execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Ошибка при получении просроченных сессий: {e}")
            return []

    async def update_button_data(self, session_id: int, button_type: str = None, 
                                button_url: str = None, button_text: str = None) -> bool:
        """
        Обновление данных кнопки в сессии
        
        Args:
            session_id (int): ID сессии
            button_type (str): Тип кнопки ('dm' или 'website')
            button_url (str): URL кнопки
            button_text (str): Текст кнопки
            
        Returns:
            bool: True если обновление успешно
        """
        try:
            update_data = {}
            
            if button_type is not None:
                update_data['button_type'] = button_type
            if button_url is not None:
                update_data['button_url'] = button_url
            if button_text is not None:
                update_data['button_text'] = button_text
            
            if not update_data:
                return True  # Нет данных для обновления
            
            result = self.supabase.table('button_post_creation_sessions').update(
                update_data
            ).eq('id', session_id).execute()
            
            if result.data:
                logger.info(f"Обновлены данные кнопки в сессии {session_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении данных кнопки в сессии {session_id}: {e}")
            return False

    async def get_session_button_data(self, session_id: int) -> Optional[Dict[str, str]]:
        """
        Получение данных кнопки из сессии
        
        Args:
            session_id (int): ID сессии
            
        Returns:
            Dict: Данные кнопки или None
        """
        try:
            result = self.supabase.table('button_post_creation_sessions').select(
                'button_type, button_url, button_text'
            ).eq('id', session_id).execute()
            
            if result.data and len(result.data) > 0:
                data = result.data[0]
                return {
                    'button_type': data.get('button_type'),
                    'button_url': data.get('button_url'),
                    'button_text': data.get('button_text')
                }
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при получении данных кнопки из сессии {session_id}: {e}")
            return None

    async def get_active_post_session_by_id(self, session_id: int) -> Optional[Dict[str, Any]]:
        """
        Получение сессии по ID
        
        Args:
            session_id (int): ID сессии
            
        Returns:
            Dict: Данные сессии или None
        """
        try:
            result = self.supabase.table('button_post_creation_sessions').select('*').eq(
                'id', session_id
            ).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при получении сессии по ID {session_id}: {e}")
            return None
