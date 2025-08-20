-- Создание таблицы пользователей для Telegram бота
-- Основная таблица для хранения информации о пользователях

CREATE TABLE button_users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    telegram_id BIGINT UNIQUE,
    username VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    registration_step INTEGER DEFAULT 0,
    -- 0: не зарегистрирован
    -- 1: email подтвержден, ожидает ссылку на канал  
    -- 2: ссылка на канал получена, ожидает подтверждения прав админа
    -- 3: полностью зарегистрирован
    channel_url VARCHAR(500),
    channel_id BIGINT,
    channel_title VARCHAR(200),
    is_bot_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы для оптимизации запросов
CREATE INDEX idx_button_users_email ON button_users(email);
CREATE INDEX idx_button_users_telegram_id ON button_users(telegram_id);
CREATE INDEX idx_button_users_registration_step ON button_users(registration_step);

-- Функция для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Триггер для автоматического обновления updated_at при изменении записи
CREATE TRIGGER update_button_users_updated_at 
    BEFORE UPDATE ON button_users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Комментарии к таблице и колонкам
COMMENT ON TABLE button_users IS 'Таблица пользователей Telegram бота';
COMMENT ON COLUMN button_users.id IS 'Уникальный идентификатор пользователя';
COMMENT ON COLUMN button_users.email IS 'Email пользователя (основной ключ для поиска)';
COMMENT ON COLUMN button_users.telegram_id IS 'Telegram ID пользователя';
COMMENT ON COLUMN button_users.registration_step IS 'Этап регистрации пользователя (0-3)';
COMMENT ON COLUMN button_users.channel_url IS 'Ссылка на канал пользователя';
COMMENT ON COLUMN button_users.channel_id IS 'ID канала в Telegram';
COMMENT ON COLUMN button_users.is_bot_admin IS 'Имеет ли бот права администратора в канале';

-- Таблица для хранения процессов создания постов
CREATE TABLE button_post_creation_sessions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES button_users(id) ON DELETE CASCADE,
    telegram_id BIGINT NOT NULL,
    session_status VARCHAR(50) DEFAULT 'started',
    -- started: начат процесс
    -- question_1: ожидает ответ на вопрос 1
    -- question_2: ожидает ответ на вопрос 2  
    -- question_3: ожидает ответ на вопрос 3
    -- generating: отправлен запрос в n8n
    -- reviewing: пост на проверке у пользователя
    -- button_type_selection: выбор типа кнопки (личка/сайт)
    -- button_config: настройка параметров кнопки
    -- button_text_selection: выбор текста кнопки
    -- final_review: финальный просмотр поста с кнопкой
    -- completed: процесс завершен
    -- cancelled: процесс отменен
    answer_1 TEXT,
    answer_2 TEXT,
    answer_3 TEXT,
    generated_post TEXT,
    button_type VARCHAR(20), -- 'dm' или 'website'
    button_url TEXT, -- ссылка для кнопки
    button_text VARCHAR(100), -- текст кнопки
    n8n_webhook_sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '1 hour')
);

-- Индексы для таблицы button_post_creation_sessions
CREATE INDEX idx_button_post_sessions_telegram_id ON button_post_creation_sessions(telegram_id);
CREATE INDEX idx_button_post_sessions_status ON button_post_creation_sessions(session_status);
CREATE INDEX idx_button_post_sessions_expires ON button_post_creation_sessions(expires_at);

-- Триггер для автоматического обновления updated_at
CREATE TRIGGER update_button_post_sessions_updated_at 
    BEFORE UPDATE ON button_post_creation_sessions 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Комментарии к таблице button_post_creation_sessions
COMMENT ON TABLE button_post_creation_sessions IS 'Сессии создания постов пользователями';
COMMENT ON COLUMN button_post_creation_sessions.session_status IS 'Статус процесса создания поста';
COMMENT ON COLUMN button_post_creation_sessions.answer_1 IS 'Ответ на первый вопрос';
COMMENT ON COLUMN button_post_creation_sessions.answer_2 IS 'Ответ на второй вопрос';
COMMENT ON COLUMN button_post_creation_sessions.answer_3 IS 'Ответ на третий вопрос';
COMMENT ON COLUMN button_post_creation_sessions.generated_post IS 'Сгенерированный n8n текст поста';
COMMENT ON COLUMN button_post_creation_sessions.button_type IS 'Тип кнопки: dm (личные сообщения) или website (сайт)';
COMMENT ON COLUMN button_post_creation_sessions.button_url IS 'URL для кнопки (ссылка на пользователя или веб-сайт)';
COMMENT ON COLUMN button_post_creation_sessions.button_text IS 'Текст кнопки';
COMMENT ON COLUMN button_post_creation_sessions.n8n_webhook_sent_at IS 'Время отправки запроса в n8n';
COMMENT ON COLUMN button_post_creation_sessions.expires_at IS 'Время истечения сессии';
