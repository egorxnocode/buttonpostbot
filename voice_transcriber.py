"""
Модуль для транскрибации голосовых сообщений через OpenAI Whisper
"""
import os
import logging
import tempfile
from typing import Optional
import aiohttp
from openai import AsyncOpenAI
from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

class VoiceTranscriber:
    def __init__(self):
        """Инициализация транскрибера"""
        if not OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY не установлен - транскрибация недоступна")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
            logger.info("OpenAI клиент инициализирован")

    async def transcribe_voice_message(self, file_url: str, bot_token: str) -> Optional[str]:
        """
        Транскрибация голосового сообщения
        
        Args:
            file_url (str): URL файла голосового сообщения
            bot_token (str): Токен бота для загрузки файла
            
        Returns:
            Optional[str]: Транскрибированный текст или None при ошибке
        """
        if not self.client:
            logger.error("OpenAI клиент не инициализирован")
            return None

        try:
            # Загружаем голосовой файл
            audio_data = await self._download_voice_file(file_url, bot_token)
            if not audio_data:
                return None

            # Создаем временный файл
            with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name

            try:
                # Транскрибируем через OpenAI Whisper
                with open(temp_file_path, "rb") as audio_file:
                    transcript = await self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language="ru"  # Указываем русский язык
                    )
                
                logger.info(f"Транскрибация успешна: {len(transcript.text)} символов")
                return transcript.text.strip()

            finally:
                # Удаляем временный файл
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        except Exception as e:
            logger.error(f"Ошибка при транскрибации: {e}")
            return None

    async def _download_voice_file(self, file_url: str, bot_token: str) -> Optional[bytes]:
        """
        Загрузка голосового файла с серверов Telegram
        
        Args:
            file_url (str): URL файла
            bot_token (str): Токен бота
            
        Returns:
            Optional[bytes]: Данные файла или None при ошибке
        """
        try:
            # Формируем полный URL для загрузки
            download_url = f"https://api.telegram.org/file/bot{bot_token}/{file_url}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(download_url) as response:
                    if response.status == 200:
                        data = await response.read()
                        logger.info(f"Загружен голосовой файл: {len(data)} байт")
                        return data
                    else:
                        logger.error(f"Ошибка загрузки файла: HTTP {response.status}")
                        return None

        except Exception as e:
            logger.error(f"Ошибка при загрузке голосового файла: {e}")
            return None

    def is_available(self) -> bool:
        """Проверка доступности транскрибации"""
        return self.client is not None
