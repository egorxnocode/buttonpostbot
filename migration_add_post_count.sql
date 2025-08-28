-- Миграция: Добавление счетчика постов для ограничения количества публикаций
-- Дата: 2024
-- Описание: Добавляет поле post_count в таблицу button_users для ограничения до 3 постов на пользователя

-- Добавляем поле post_count в таблицу button_users
ALTER TABLE button_users 
ADD COLUMN post_count INTEGER DEFAULT 0 NOT NULL;

-- Добавляем комментарий к новому полю
COMMENT ON COLUMN button_users.post_count IS 'Количество опубликованных постов пользователем (макс. 3)';

-- Создаем индекс для быстрой проверки количества постов
CREATE INDEX idx_button_users_post_count ON button_users(post_count);

-- Обновляем существующих пользователей - устанавливаем счетчик в 0
UPDATE button_users SET post_count = 0 WHERE post_count IS NULL;

-- Проверочный запрос для подтверждения изменений
-- SELECT email, post_count FROM button_users LIMIT 5;
