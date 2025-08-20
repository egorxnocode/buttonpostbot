"""
Утилиты для Telegram бота
"""
import re
import logging
from typing import Optional, Tuple
import validators

logger = logging.getLogger(__name__)

def extract_email_from_text(text: str) -> Optional[str]:
    """
    Извлечение email из текста в любом формате
    
    Args:
        text (str): Текст сообщения пользователя
        
    Returns:
        Optional[str]: Email в нижнем регистре или None если не найден
    """
    # Регулярное выражение для поиска email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    # Ищем все email в тексте
    emails = re.findall(email_pattern, text, re.IGNORECASE)
    
    if emails:
        # Берем первый найденный email и приводим к нижнему регистру
        email = emails[0].lower().strip()
        
        # Дополнительная проверка валидности email
        if validators.email(email):
            logger.info(f"Email извлечен из текста: {email}")
            return email
        else:
            logger.warning(f"Найденный email не прошел валидацию: {email}")
            return None
    
    logger.info("Email не найден в тексте")
    return None

def is_valid_email(email: str) -> bool:
    """
    Проверка валидности email адреса
    
    Args:
        email (str): Email для проверки
        
    Returns:
        bool: True если email валиден
    """
    return validators.email(email)

def extract_channel_info(text: str) -> Optional[Tuple[str, str]]:
    """
    Извлечение информации о канале из текста
    
    Args:
        text (str): Текст с ссылкой на канал
        
    Returns:
        Optional[Tuple[str, str]]: (channel_username, normalized_url) или None
    """
    text = text.strip()
    
    # Паттерны для различных форматов ссылок на каналы
    patterns = [
        r't\.me/([a-zA-Z0-9_]+)',  # https://t.me/channel_name
        r'@([a-zA-Z0-9_]+)',       # @channel_name
        r'telegram\.me/([a-zA-Z0-9_]+)'  # telegram.me/channel_name
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            username = match.group(1)
            normalized_url = f"https://t.me/{username}"
            logger.info(f"Извлечена информация о канале: @{username}")
            return username, normalized_url
    
    logger.info("Ссылка на канал не найдена в тексте")
    return None

def is_valid_channel_url(url: str) -> bool:
    """
    Проверка валидности URL канала
    
    Args:
        url (str): URL для проверки
        
    Returns:
        bool: True если URL валиден
    """
    # Проверяем базовую валидность URL
    if not validators.url(url):
        return False
    
    # Проверяем что это ссылка на Telegram
    telegram_domains = ['t.me', 'telegram.me']
    
    for domain in telegram_domains:
        if domain in url.lower():
            return True
    
    return False

def format_user_info(user) -> str:
    """
    Форматирование информации о пользователе для логов
    
    Args:
        user: Объект User из python-telegram-bot или dict
        
    Returns:
        str: Отформатированная строка
    """
    # Если это объект User из telegram, извлекаем атрибуты
    if hasattr(user, 'first_name'):
        first_name = user.first_name
        last_name = getattr(user, 'last_name', None)
        username = getattr(user, 'username', None)
        user_id = getattr(user, 'id', 'N/A')
    # Если это словарь
    elif isinstance(user, dict):
        first_name = user.get('first_name')
        last_name = user.get('last_name')
        username = user.get('username')
        user_id = user.get('telegram_id', user.get('id', 'N/A'))
    else:
        return str(user)
    
    name_parts = []
    if first_name:
        name_parts.append(first_name)
    if last_name:
        name_parts.append(last_name)
    
    name = ' '.join(name_parts) if name_parts else 'Без имени'
    username_str = f"@{username}" if username else 'Без username'
    
    return f"{name} ({username_str}) [ID: {user_id}]"

def get_registration_step_name(step: int) -> str:
    """
    Получение названия этапа регистрации
    
    Args:
        step (int): Номер этапа
        
    Returns:
        str: Название этапа
    """
    step_names = {
        0: "Не зарегистрирован",
        1: "Email подтвержден",
        2: "Канал добавлен", 
        3: "Регистрация завершена"
    }
    
    return step_names.get(step, f"Неизвестный этап ({step})")

def clean_text(text: str) -> str:
    """
    Очистка текста от лишних символов и пробелов
    
    Args:
        text (str): Исходный текст
        
    Returns:
        str: Очищенный текст
    """
    if not text:
        return ""
    
    # Убираем лишние пробелы и переносы строк
    cleaned = re.sub(r'\s+', ' ', text.strip())
    
    return cleaned
