#!/usr/bin/env python3
"""
Скрипт для тестирования подключения к Supabase и основных функций
"""
import asyncio
import sys
from database import Database
from config import SUPABASE_URL, SUPABASE_KEY

async def test_connection():
    """Тестирование подключения к базе данных"""
    
    print("🔍 Тестирование подключения к Supabase...")
    
    # Проверяем наличие конфигурации
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Ошибка: SUPABASE_URL или SUPABASE_KEY не установлены")
        print("Проверьте файл .env")
        return False
    
    try:
        # Создаем подключение к БД
        db = Database()
        print("✅ Подключение к Supabase установлено")
        
        # Тестируем поиск пользователя (который не существует)
        test_email = "test@example.com"
        user = await db.find_user_by_email(test_email)
        
        if user:
            print(f"✅ Найден тестовый пользователь: {user['email']}")
        else:
            print(f"ℹ️  Пользователь {test_email} не найден (это нормально для тестирования)")
        
        print("✅ Все тесты пройдены успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return False

async def main():
    """Главная функция"""
    print("🤖 Тестирование Telegram бота")
    print("=" * 50)
    
    success = await test_connection()
    
    if success:
        print("\n✅ Все проверки пройдены!")
        print("Теперь вы можете запустить бота командой: python bot.py")
    else:
        print("\n❌ Обнаружены проблемы!")
        print("Проверьте настройки в файле .env")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
