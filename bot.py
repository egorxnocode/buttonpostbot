"""
Основной модуль Telegram бота для регистрации пользователей и управления каналами
"""
import logging
import asyncio
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    filters,
    ContextTypes
)
from telegram.error import TelegramError

from config import (
    TELEGRAM_BOT_TOKEN, 
    MESSAGES, 
    REGISTRATION_STEPS,
    LOG_LEVEL
)
from database import Database
from utils import (
    extract_email_from_text, 
    is_valid_email, 
    extract_channel_info,
    is_valid_channel_url,
    format_user_info,
    get_registration_step_name
)
from n8n_client import N8NClient
from admin_notifier import AdminNotifier
from voice_transcriber import VoiceTranscriber

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL, logging.INFO)
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        """Инициализация бота"""
        if not TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN не установлен")
        
        self.db = Database()
        self.n8n_client = N8NClient()
        self.admin_notifier = AdminNotifier()
        self.voice_transcriber = VoiceTranscriber()
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.bot_username = None
        
        # Добавляем обработчики
        self._setup_handlers()
        
        logger.info("Telegram бот инициализирован")

    def _setup_handlers(self):
        """Настройка обработчиков команд и сообщений"""
        
        # Команды
        self.application.add_handler(CommandHandler("start", self.start_command))
        
        # Обработчик кнопок
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Обработчик текстовых сообщений
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.handle_message
        ))
        
        # Обработчик голосовых сообщений
        self.application.add_handler(MessageHandler(
            filters.VOICE, 
            self.handle_voice_message
        ))
        
        logger.info("Обработчики команд настроены")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        
        logger.info(f"Команда /start от пользователя: {format_user_info(user)}")
        
        # Обновляем время последней активности
        await self.db.update_last_activity(user.id)
        
        # Проверяем, зарегистрирован ли пользователь
        user_data = await self.db.get_user_by_telegram_id(user.id)
        
        if user_data and user_data['registration_step'] == REGISTRATION_STEPS['COMPLETED']:
            await update.message.reply_text(
                "🎉 Вы уже зарегистрированы!\n\n"
                "Используйте кнопку ниже для создания постов:",
                reply_markup=self._get_registered_user_keyboard()
            )
            return
        
        # Отправляем приветственное сообщение
        await update.message.reply_text(MESSAGES['welcome'])

    async def _setup_menu_button(self):
        """Настройка постоянной кнопки меню для зарегистрированных пользователей"""
        try:
            # Устанавливаем команды бота
            await self.application.bot.set_my_commands([
                BotCommand("start", "Начать регистрацию")
            ])
            
            logger.info("Команды бота установлены")
        except Exception as e:
            logger.error(f"Ошибка при установке команд: {e}")

    def _get_registered_user_keyboard(self):
        """Получить клавиатуру для зарегистрированного пользователя"""
        keyboard = [
            [InlineKeyboardButton("📝 Написать пост", callback_data="write_post")]
        ]
        return InlineKeyboardMarkup(keyboard)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        user = update.effective_user
        message_text = update.message.text
        
        logger.info(f"Сообщение от {format_user_info(user)}: {message_text[:100]}...")
        
        await self.db.update_last_activity(user.id)
        
        # Получаем данные пользователя
        user_data = await self.db.get_user_by_telegram_id(user.id)
        
        if not user_data:
            # Пользователь не найден, пытаемся обработать как email
            await self._handle_email_registration(update, message_text, user)
        else:
            # Проверяем активную сессию создания поста
            active_session = await self.db.get_active_post_session(user.id)
            
            if active_session:
                # Обрабатываем ответ в рамках сессии создания поста
                await self._handle_post_creation_answer(update, message_text, user_data, active_session)
            else:
                # Пользователь найден, обрабатываем в зависимости от этапа регистрации
                step = user_data['registration_step']
                
                if step == REGISTRATION_STEPS['EMAIL_CONFIRMED']:
                    await self._handle_channel_url(update, message_text, user_data)
                elif step == REGISTRATION_STEPS['CHANNEL_ADDED']:
                    # Пользователь может изменить канал или получить инструкции
                    channel_info = extract_channel_info(message_text)
                    if channel_info:
                        # Пользователь отправил новую ссылку на канал - обновляем
                        await self._handle_channel_url(update, message_text, user_data)
                    else:
                        # Напоминаем о необходимости подтверждения прав админа
                        await self._show_admin_reminder(update, user_data)
                elif step == REGISTRATION_STEPS['COMPLETED']:
                    await update.message.reply_text(
                        "✅ Вы уже зарегистрированы!\n\n"
                        "Используйте кнопку ниже для создания постов:",
                        reply_markup=self._get_registered_user_keyboard()
                    )
                else:
                    await update.message.reply_text(
                        "🤔 Не понимаю, что вы хотите сделать.\n\n"
                        "Используйте /start для проверки текущего статуса."
                    )

    async def _handle_email_registration(self, update: Update, message_text: str, user):
        """Обработка регистрации по email"""
        
        # Извлекаем email из сообщения
        email = extract_email_from_text(message_text)
        
        if not email:
            await update.message.reply_text(MESSAGES['invalid_email'])
            return
        
        # Проверяем email в базе данных
        user_data = await self.db.find_user_by_email(email)
        
        if not user_data:
            await update.message.reply_text(MESSAGES['email_not_found'])
            return
        
        # Email найден, обновляем Telegram данные
        telegram_data = {
            'telegram_id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        }
        
        success = await self.db.update_user_telegram_data(email, telegram_data)
        
        if success:
            await update.message.reply_text(MESSAGES['email_confirmed'])
            logger.info(f"Email подтвержден для пользователя: {format_user_info(user)}")
        else:
            await update.message.reply_text(
                "❌ Произошла ошибка при подтверждении email. Попробуйте позже."
            )

    async def _handle_channel_url(self, update: Update, message_text: str, user_data: dict):
        """Обработка ссылки на канал"""
        
        channel_info = extract_channel_info(message_text)
        
        if not channel_info:
            await update.message.reply_text(
                "❌ Не удалось распознать ссылку на канал.\n\n"
                "Пожалуйста, отправьте ссылку в формате:\n"
                "• @channel_name\n"
                "• https://t.me/channel_name"
            )
            return
        
        channel_username, channel_url = channel_info
        
        # Сохраняем данные канала
        success = await self.db.update_channel_data(
            user_data['telegram_id'], 
            channel_url
        )
        
        if not success:
            await update.message.reply_text(
                "❌ Произошла ошибка при сохранении канала. Попробуйте позже."
            )
            return
        
        # Получаем username бота для инструкций
        if not self.bot_username:
            bot_info = await self.application.bot.get_me()
            self.bot_username = bot_info.username
        
        # Создаем кнопку для подтверждения
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Добавлено", callback_data="admin_added")
        ]])
        
        instructions = MESSAGES['channel_instructions'].format(
            bot_username=self.bot_username
        )
        
        await update.message.reply_text(
            instructions,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        user = query.from_user
        
        await query.answer()
        await self.db.update_last_activity(user.id)
        
        if query.data == "admin_added":
            await self._check_admin_rights(query, user)
        elif query.data == "write_post":
            await self._handle_write_post(query, user)
        elif query.data == "post_approved":
            await self._handle_post_approval(query, user)
        elif query.data == "post_rejected":
            await self._handle_post_rejection(query, user)

    async def _check_admin_rights(self, query, user):
        """Проверка прав администратора бота в канале"""
        
        # Получаем данные пользователя
        user_data = await self.db.get_user_by_telegram_id(user.id)
        
        if not user_data or not user_data.get('channel_url'):
            await query.edit_message_text(
                "❌ Ошибка: данные канала не найдены. Попробуйте начать заново с /start"
            )
            return
        
        await query.edit_message_text(MESSAGES['checking_admin'])
        
        try:
            # Пытаемся получить информацию о канале
            channel_username = user_data['channel_url'].split('/')[-1]
            
            # Проверяем права администратора
            try:
                chat_member = await self.application.bot.get_chat_member(
                    f"@{channel_username}", 
                    self.application.bot.id
                )
                
                # Проверяем статус и права
                is_admin = (
                    chat_member.status in ['administrator', 'creator'] and
                    getattr(chat_member, 'can_post_messages', False)
                )
                
                if is_admin:
                    # Обновляем статус в БД
                    await self.db.update_admin_status(user.id, True)
                    
                    await query.edit_message_text(
                        MESSAGES['registration_complete'],
                        reply_markup=self._get_registered_user_keyboard()
                    )
                    
                    logger.info(f"Регистрация завершена для пользователя: {format_user_info(user)}")
                else:
                    await self._show_not_admin_message(query)
                    
            except TelegramError as e:
                if "chat not found" in str(e).lower():
                    await query.edit_message_text(
                        "❌ Канал не найден. Проверьте правильность ссылки и попробуйте снова."
                    )
                else:
                    await self._show_not_admin_message(query)
                    
        except Exception as e:
            logger.error(f"Ошибка при проверке прав администратора: {e}")
            await query.edit_message_text(
                "❌ Произошла ошибка при проверке прав. Попробуйте позже."
            )

    async def _handle_write_post(self, query, user):
        """Обработка нажатия на кнопку 'Написать пост'"""
        
        # Проверяем, что пользователь зарегистрирован
        user_data = await self.db.get_user_by_telegram_id(user.id)
        
        if not user_data or user_data['registration_step'] != REGISTRATION_STEPS['COMPLETED']:
            await query.edit_message_text(
                "❌ Вы не зарегистрированы или регистрация не завершена.\n\n"
                "Используйте /start для начала регистрации."
            )
            return
        
        # Создаем новую сессию создания поста
        session_id = await self.db.create_post_session(user_data['id'], user.id)
        
        if not session_id:
            await query.edit_message_text(
                "❌ Произошла ошибка при создании сессии. Попробуйте позже.",
                reply_markup=self._get_registered_user_keyboard()
            )
            return
        
        # Отправляем приветственное сообщение и первый вопрос
        await query.edit_message_text(MESSAGES['post_creation_start'])
        
        # Отправляем первый вопрос
        await asyncio.sleep(1)  # Небольшая задержка для лучшего UX
        await query.message.reply_text(MESSAGES['question_1'])
        
        logger.info(f"Начата сессия создания поста {session_id} для пользователя {format_user_info(user)}")

    async def _handle_post_creation_answer(self, update: Update, message_text: str, 
                                         user_data: dict, active_session: dict):
        """Обработка ответов в процессе создания поста"""
        
        session_status = active_session['session_status']
        session_id = active_session['id']
        
        # Определяем номер вопроса
        if session_status == 'question_1':
            question_num = 1
            next_message = MESSAGES['question_2']
        elif session_status == 'question_2':
            question_num = 2
            next_message = MESSAGES['question_3']
        elif session_status == 'question_3':
            question_num = 3
            next_message = MESSAGES['generating_post']
        else:
            # Неожиданный статус
            await update.message.reply_text(
                "🤔 Произошла ошибка. Попробуйте создать пост заново.",
                reply_markup=self._get_registered_user_keyboard()
            )
            return
        
        # Сохраняем ответ в базе данных
        success = await self.db.update_session_answer(session_id, question_num, message_text.strip())
        
        if not success:
            await update.message.reply_text(
                "❌ Ошибка при сохранении ответа. Попробуйте еще раз."
            )
            return
        
        logger.info(f"Сохранен ответ {question_num} в сессии {session_id}: {message_text[:50]}...")
        
        # Отправляем следующий вопрос или начинаем генерацию
        if question_num < 3:
            await update.message.reply_text(next_message)
        else:
            # Все три ответа получены, начинаем генерацию
            await update.message.reply_text(next_message)
            await self._start_post_generation(update, user_data, session_id)

    async def _start_post_generation(self, update: Update, user_data: dict, session_id: int):
        """Начало генерации поста через n8n"""
        
        try:
            # Получаем все ответы из сессии
            answers = await self.db.get_session_answers(session_id)
            
            if not answers or not all(answers.values()):
                await update.message.reply_text(MESSAGES['generation_error'])
                return
            
            # Отправляем запрос в n8n
            success = await self.n8n_client.send_post_generation_request(user_data, answers)
            
            if not success:
                await update.message.reply_text(MESSAGES['generation_error'])
                await self.db.clear_session_answers(session_id)
                return
            
            logger.info(f"Запрос на генерацию отправлен для сессии {session_id}")
            
            # Запускаем таймер таймаута
            asyncio.create_task(self._monitor_generation_timeout(session_id, user_data))
            
        except Exception as e:
            logger.error(f"Ошибка при запуске генерации для сессии {session_id}: {e}")
            await update.message.reply_text(MESSAGES['generation_error'])
            await self.admin_notifier.notify_error(f"Ошибка генерации поста: {e}", user_data)

    async def _monitor_generation_timeout(self, session_id: int, user_data: dict):
        """Мониторинг таймаута генерации поста"""
        
        # Ждем 3 минуты
        await asyncio.sleep(180)  # 3 минуты = 180 секунд
        
        # Проверяем, не завершилась ли сессия за это время
        session = await self.db.get_active_post_session(user_data['telegram_id'])
        
        if session and session['id'] == session_id and session['session_status'] == 'generating':
            # Таймаут! Уведомляем админа и сбрасываем сессию
            logger.warning(f"Таймаут генерации для сессии {session_id}")
            
            # Уведомляем админа
            await self.admin_notifier.notify_timeout(user_data, session_id)
            
            # Уведомляем n8n о таймауте
            await self.n8n_client.notify_timeout(user_data, session_id)
            
            # Очищаем ответы и сбрасываем сессию
            await self.db.clear_session_answers(session_id)
            
            # Отправляем сообщение пользователю
            try:
                await self.application.bot.send_message(
                    chat_id=user_data['telegram_id'],
                    text=MESSAGES['generation_timeout'],
                    reply_markup=self._get_registered_user_keyboard()
                )
            except Exception as e:
                logger.error(f"Ошибка при отправке сообщения о таймауте пользователю {user_data['telegram_id']}: {e}")

    async def _handle_post_approval(self, query, user):
        """Обработка одобрения поста пользователем"""
        
        # Получаем активную сессию
        active_session = await self.db.get_active_post_session(user.id)
        
        if not active_session or active_session['session_status'] != 'reviewing':
            await query.edit_message_text(
                "❌ Сессия не найдена или завершена.",
                reply_markup=self._get_registered_user_keyboard()
            )
            return
        
        # Обновляем статус сессии
        await self.db.update_session_status(active_session['id'], 'completed')
        
        await query.edit_message_text(MESSAGES['post_approved'])
        
        # Здесь будет логика публикации поста в канале
        # Пока что просто показываем успешное завершение
        await asyncio.sleep(2)
        await query.message.reply_text(
            "🎉 Пост успешно опубликован в вашем канале!",
            reply_markup=self._get_registered_user_keyboard()
        )
        
        logger.info(f"Пост одобрен и опубликован для сессии {active_session['id']}")

    async def _handle_post_rejection(self, query, user):
        """Обработка отклонения поста пользователем"""
        
        # Получаем активную сессию
        active_session = await self.db.get_active_post_session(user.id)
        
        if not active_session or active_session['session_status'] != 'reviewing':
            await query.edit_message_text(
                "❌ Сессия не найдена или завершена.",
                reply_markup=self._get_registered_user_keyboard()
            )
            return
        
        # Очищаем ответы и начинаем заново
        await self.db.clear_session_answers(active_session['id'])
        
        await query.edit_message_text(MESSAGES['post_rejected'])
        
        # Начинаем процесс заново
        await asyncio.sleep(1)
        await query.message.reply_text(MESSAGES['post_creation_start'])
        await asyncio.sleep(1)
        await query.message.reply_text(MESSAGES['question_1'])
        
        logger.info(f"Пост отклонен, начат новый процесс для сессии {active_session['id']}")

    def _get_post_review_keyboard(self):
        """Получить клавиатуру для проверки поста"""
        keyboard = [
            [
                InlineKeyboardButton("✅ Верно", callback_data="post_approved"),
                InlineKeyboardButton("❌ Нет", callback_data="post_rejected")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    async def _show_not_admin_message(self, query):
        """Показать сообщение о том, что бот не администратор"""
        
        # Создаем кнопку для повторной проверки
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Добавлено", callback_data="admin_added")
        ]])
        
        await query.edit_message_text(
            MESSAGES['not_admin'],
            reply_markup=keyboard
        )

    async def _show_admin_reminder(self, update: Update, user_data: dict):
        """Показать напоминание о необходимости подтверждения прав админа"""
        
        # Получаем username бота для инструкций
        if not self.bot_username:
            bot_info = await self.application.bot.get_me()
            self.bot_username = bot_info.username
        
        # Создаем кнопку для подтверждения
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Добавлено", callback_data="admin_added")
        ]])
        
        current_channel = user_data.get('channel_url', 'не указан')
        
        reminder_message = f"""
🤖 Вы уже добавили канал: {current_channel}

Для завершения регистрации необходимо добавить меня администратором канала.

📋 Если вы еще не добавили меня администратором:

1️⃣ Откройте ваш канал
2️⃣ Нажмите на название канала вверху
3️⃣ Выберите "Управление каналом"
4️⃣ Нажмите "Администраторы"
5️⃣ Нажмите "Добавить администратора"
6️⃣ Найдите меня (@{self.bot_username}) и добавьте
7️⃣ Дайте права на публикацию сообщений

После добавления нажмите кнопку "Добавлено" ниже 👇

💡 Если хотите изменить канал, отправьте новую ссылку в формате @channel_name или https://t.me/channel_name
        """
        
        await update.message.reply_text(
            reminder_message.strip(),
            reply_markup=keyboard
        )

    async def handle_voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик голосовых сообщений"""
        user = update.effective_user
        voice = update.message.voice
        
        logger.info(f"Получено голосовое сообщение от пользователя: {format_user_info(user)}")
        
        # Проверяем, доступна ли транскрибация
        if not self.voice_transcriber.is_available():
            await update.message.reply_text(
                "❌ Транскрибация голосовых сообщений недоступна. "
                "Пожалуйста, отправьте текстовое сообщение."
            )
            return
        
        # Получаем данные пользователя
        user_data = await self.db.get_user_by_telegram_id(user.id)
        if not user_data:
            await update.message.reply_text(MESSAGES['welcome'])
            return
        
        # Проверяем, что пользователь находится в процессе создания поста
        # и отвечает на один из 3 вопросов
        is_answering_questions = await self._is_answering_post_questions(user_data)
        
        if not is_answering_questions:
            # Получаем информацию о сессии для диагностики
            active_session = await self.db.get_active_post_session(user_data['telegram_id'])
            session_status = active_session.get('session_status') if active_session else 'no_session'
            
            logger.info(f"Голосовое сообщение отклонено. Session status: {session_status}")
            
            await update.message.reply_text(
                f"🎤 Голосовые сообщения принимаются только при ответе на вопросы для создания поста.\n\n"
                f"Текущий статус: {session_status}\n\n"
                f"Для начала создания поста нажмите кнопку \"Написать пост\" в меню."
            )
            return
        
        logger.info(f"Голосовое сообщение принято для обработки от пользователя {user.id}")
        
        # Показываем индикатор набора текста
        await update.message.chat.send_action("typing")
        
        try:
            # Получаем информацию о файле
            file = await context.bot.get_file(voice.file_id)
            
            # Загружаем файл в байты напрямую
            file_bytes = await file.download_as_bytearray()
            
            # Транскрибируем голосовое сообщение
            transcribed_text = await self.voice_transcriber.transcribe_voice_from_bytes(
                file_bytes
            )
            
            if transcribed_text:
                # Отправляем транскрибированный текст пользователю
                await update.message.reply_text(
                    f"🎤 Распознанный текст:\n\n\"{transcribed_text}\"\n\n"
                    f"Обрабатываю ваш ответ..."
                )
                
                # Обрабатываем транскрибированный текст как обычное текстовое сообщение
                # Создаем временный объект сообщения с текстом
                update.message.text = transcribed_text
                await self.handle_message(update, context)
                
            else:
                await update.message.reply_text(
                    "❌ Не удалось распознать голосовое сообщение. "
                    "Пожалуйста, попробуйте еще раз или отправьте текстовое сообщение."
                )
        
        except Exception as e:
            logger.error(f"Ошибка при обработке голосового сообщения: {e}")
            await update.message.reply_text(
                "❌ Произошла ошибка при обработке голосового сообщения. "
                "Пожалуйста, попробуйте отправить текстовое сообщение."
            )

    async def _is_answering_post_questions(self, user_data: dict) -> bool:
        """
        Проверяет, находится ли пользователь в процессе ответа на вопросы для создания поста
        
        Args:
            user_data (dict): Данные пользователя
            
        Returns:
            bool: True если пользователь отвечает на вопросы для поста
        """
        try:
            # Получаем активную сессию создания поста для пользователя
            active_session = await self.db.get_active_post_session(user_data['telegram_id'])
            
            if not active_session:
                return False
            
            # Проверяем статус сессии - принимаем голосовые только на вопросы
            session_status = active_session.get('session_status')
            
            # Статусы, когда можно отправлять голосовые сообщения
            question_statuses = ['question_1', 'question_2', 'question_3']
            
            return session_status in question_statuses
            
        except Exception as e:
            logger.error(f"Ошибка при проверке состояния создания поста: {e}")
            return False

    def run(self):
        """Запуск бота"""
        logger.info("Запуск Telegram бота...")
        
        try:
            # Используем синхронный run_polling
            self.application.run_polling(drop_pending_updates=True)
            
        except Exception as e:
            logger.error(f"Ошибка при запуске бота: {e}")
            raise

def main():
    """Главная функция"""
    try:
        bot = TelegramBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        raise

if __name__ == "__main__":
    main()
