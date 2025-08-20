#!/bin/bash

# Скрипт для проверки сетевого соединения

echo "🌐 Проверка сетевого соединения..."

# Проверяем базовое подключение к интернету
echo "📡 Тестируем подключение к Google DNS..."
if ping -c 3 8.8.8.8 > /dev/null 2>&1; then
    echo "✅ Ping до 8.8.8.8 работает"
else
    echo "❌ Ping до 8.8.8.8 не работает"
fi

# Проверяем DNS разрешение
echo "🔍 Тестируем DNS разрешение..."
if nslookup google.com > /dev/null 2>&1; then
    echo "✅ DNS разрешение работает"
else
    echo "❌ DNS разрешение не работает"
fi

# Проверяем HTTPS соединения
echo "🔒 Тестируем HTTPS соединения..."

urls=("https://api.telegram.org" "https://supabase.co" "https://google.com")

for url in "${urls[@]}"; do
    if curl -s --connect-timeout 5 "$url" > /dev/null; then
        echo "✅ Доступ к $url работает"
    else
        echo "❌ Доступ к $url не работает"
    fi
done

# Проверяем доступность Telegram API с токенами
echo "🤖 Тестируем Telegram API..."
if [ -f ".env" ]; then
    # Проверяем основной токен бота
    if grep -q "TELEGRAM_BOT_TOKEN=" .env; then
        token=$(grep "TELEGRAM_BOT_TOKEN=" .env | cut -d'=' -f2 | tr -d ' ')
        if [ -n "$token" ]; then
            echo "🔍 Проверяем основной токен бота..."
            response=$(curl -s "https://api.telegram.org/bot$token/getMe")
            if echo "$response" | grep -q '"ok":true'; then
                bot_username=$(echo "$response" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
                echo "✅ Основной токен работает (@$bot_username)"
            else
                echo "❌ Основной токен неверный или бот заблокирован"
                echo "   Ответ API: $response"
            fi
        else
            echo "⚠️  Основной токен пустой"
        fi
    else
        echo "❌ TELEGRAM_BOT_TOKEN не найден в .env"
    fi
    
    # Проверяем админский токен (опционально)
    if grep -q "ADMIN_BOT_TOKEN=" .env; then
        admin_token=$(grep "ADMIN_BOT_TOKEN=" .env | cut -d'=' -f2 | tr -d ' ')
        if [ -n "$admin_token" ]; then
            echo "🔍 Проверяем админский токен бота..."
            admin_response=$(curl -s "https://api.telegram.org/bot$admin_token/getMe")
            if echo "$admin_response" | grep -q '"ok":true'; then
                admin_bot_username=$(echo "$admin_response" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
                echo "✅ Админский токен работает (@$admin_bot_username)"
            else
                echo "⚠️  Админский токен неверный (не критично)"
            fi
        else
            echo "ℹ️  Админский токен не задан (опционально)"
        fi
    fi
else
    echo "❌ Файл .env не найден!"
fi

echo ""
echo "🔧 Если есть проблемы с сетью:"
echo "1. Проверьте настройки фаервола"
echo "2. Убедитесь, что сервер имеет доступ к интернету"
echo "3. Проверьте DNS настройки (/etc/resolv.conf)"
echo "4. Обратитесь к администратору сервера"
