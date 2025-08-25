-- Миграция для добавления поддержки 6 вопросов вместо 3 + сбор ссылок
-- Запустить в Supabase SQL Editor

-- Добавляем новые колонки для ответов 4, 5, 6
ALTER TABLE button_post_creation_sessions 
ADD COLUMN IF NOT EXISTS answer_4 TEXT,
ADD COLUMN IF NOT EXISTS answer_5 TEXT,
ADD COLUMN IF NOT EXISTS answer_6 TEXT;

-- Добавляем колонки для ссылок (до 5 штук)
ALTER TABLE button_post_creation_sessions 
ADD COLUMN IF NOT EXISTS link_1 TEXT,
ADD COLUMN IF NOT EXISTS link_2 TEXT,
ADD COLUMN IF NOT EXISTS link_3 TEXT,
ADD COLUMN IF NOT EXISTS link_4 TEXT,
ADD COLUMN IF NOT EXISTS link_5 TEXT;

-- Обновляем комментарии в схеме
COMMENT ON COLUMN button_post_creation_sessions.answer_4 IS 'Ответ на вопрос 4: Какую основную услугу или продукт вы предлагаете для начала работы?';
COMMENT ON COLUMN button_post_creation_sessions.answer_5 IS 'Ответ на вопрос 5: От чего вы помогаете избавиться или что исключаете из процесса работы?';
COMMENT ON COLUMN button_post_creation_sessions.answer_6 IS 'Ответ на вопрос 6: Назовите 3-5 ваших самых популярных постов с названиями и ссылками';

COMMENT ON COLUMN button_post_creation_sessions.link_1 IS 'Первая ссылка пользователя';
COMMENT ON COLUMN button_post_creation_sessions.link_2 IS 'Вторая ссылка пользователя';
COMMENT ON COLUMN button_post_creation_sessions.link_3 IS 'Третья ссылка пользователя';
COMMENT ON COLUMN button_post_creation_sessions.link_4 IS 'Четвертая ссылка пользователя';
COMMENT ON COLUMN button_post_creation_sessions.link_5 IS 'Пятая ссылка пользователя';

-- Проверяем что все колонки добавились
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'button_post_creation_sessions' 
AND (column_name LIKE 'answer_%' OR column_name LIKE 'link_%')
ORDER BY column_name;
