-- Миграция для обновления ссылок на материалы с описанием
-- Запустить в Supabase SQL Editor

-- Изменяем тип данных полей ссылок на JSONB для хранения описания + URL
-- Если в полях уже есть данные - они будут преобразованы автоматически

-- Обновляем комментарии к полям
COMMENT ON COLUMN button_post_creation_sessions.link_1 IS 'Материал 1: JSON с описанием и ссылкой {"description": "...", "url": "..."}';
COMMENT ON COLUMN button_post_creation_sessions.link_2 IS 'Материал 2: JSON с описанием и ссылкой {"description": "...", "url": "..."}';
COMMENT ON COLUMN button_post_creation_sessions.link_3 IS 'Материал 3: JSON с описанием и ссылкой {"description": "...", "url": "..."}';
COMMENT ON COLUMN button_post_creation_sessions.link_4 IS 'Материал 4: JSON с описанием и ссылкой {"description": "...", "url": "..."}';
COMMENT ON COLUMN button_post_creation_sessions.link_5 IS 'Материал 5: JSON с описанием и ссылкой {"description": "...", "url": "..."}';

-- Проверяем структуру полей
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'button_post_creation_sessions' 
AND column_name LIKE 'link_%'
ORDER BY column_name;

-- Примеры валидного JSON для материалов:
-- {"description": "5 секретов быстрого похудения", "url": "https://t.me/channel/post123"}
-- {"description": "Бесплатный вебинар по маркетингу", "url": "https://example.com/webinar"}
