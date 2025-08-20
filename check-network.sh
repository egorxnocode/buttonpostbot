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

# Проверяем доступность Telegram API с токеном
echo "🤖 Тестируем Telegram API..."
if [ -f ".env" ] && grep -q "TELEGRAM_BOT_TOKEN=" .env; then
    token=$(grep "TELEGRAM_BOT_TOKEN=" .env | cut -d'=' -f2)
    if [ -n "$token" ]; then
        response=$(curl -s "https://api.telegram.org/bot$token/getMe")
        if echo "$response" | grep -q '"ok":true'; then
            echo "✅ Telegram API доступен"
        else
            echo "❌ Telegram API недоступен или неверный токен"
        fi
    else
        echo "⚠️  Токен бота пустой"
    fi
else
    echo "⚠️  Файл .env не найден"
fi

echo ""
echo "🔧 Если есть проблемы с сетью:"
echo "1. Проверьте настройки фаервола"
echo "2. Убедитесь, что сервер имеет доступ к интернету"
echo "3. Проверьте DNS настройки (/etc/resolv.conf)"
echo "4. Обратитесь к администратору сервера"
