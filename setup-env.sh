#!/bin/bash

# Скрипт для настройки .env файла

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}⚙️  Настройка .env файла для Telegram бота${NC}"
echo "=================================================="

# Проверяем, существует ли уже .env
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Файл .env уже существует!${NC}"
    echo -n "Хотите пересоздать его? (y/N): "
    read -r answer
    if [[ ! "$answer" =~ ^[Yy]$ ]]; then
        echo "Отменено. Используйте nano .env для ручного редактирования."
        exit 0
    fi
    mv .env .env.backup
    echo -e "${GREEN}✅ Создан backup: .env.backup${NC}"
fi

# Копируем шаблон
cp env.example .env

echo ""
echo -e "${BLUE}📝 Заполните обязательные параметры:${NC}"
echo ""

# Запрашиваем основной токен бота
echo -e "${YELLOW}1. Основной токен Telegram бота:${NC}"
echo "   Получите у @BotFather через команду /newbot"
echo -n "   Введите токен: "
read -r bot_token

if [ -n "$bot_token" ]; then
    sed -i.tmp "s/your_main_bot_token_here/$bot_token/" .env
    rm .env.tmp 2>/dev/null || true
    echo -e "${GREEN}   ✅ Основной токен сохранен${NC}"
else
    echo -e "${RED}   ❌ Токен не может быть пустым!${NC}"
    exit 1
fi

# Запрашиваем Supabase URL
echo ""
echo -e "${YELLOW}2. Supabase URL:${NC}"
echo "   Найдите в Project Settings > API > URL"
echo -n "   Введите URL: "
read -r supabase_url

if [ -n "$supabase_url" ]; then
    sed -i.tmp "s|https://your-project.supabase.co|$supabase_url|" .env
    rm .env.tmp 2>/dev/null || true
    echo -e "${GREEN}   ✅ Supabase URL сохранен${NC}"
else
    echo -e "${RED}   ❌ URL не может быть пустым!${NC}"
    exit 1
fi

# Запрашиваем Supabase Key
echo ""
echo -e "${YELLOW}3. Supabase Anon Key:${NC}"
echo "   Найдите в Project Settings > API > anon/public key"
echo -n "   Введите ключ: "
read -r supabase_key

if [ -n "$supabase_key" ]; then
    sed -i.tmp "s/your_supabase_anon_key_here/$supabase_key/" .env
    rm .env.tmp 2>/dev/null || true
    echo -e "${GREEN}   ✅ Supabase ключ сохранен${NC}"
else
    echo -e "${RED}   ❌ Ключ не может быть пустым!${NC}"
    exit 1
fi

# Запрашиваем N8N webhook URL
echo ""
echo -e "${YELLOW}4. n8n Webhook URL:${NC}"
echo "   URL webhook эндпоинта для генерации постов"
echo -n "   Введите URL: "
read -r n8n_url

if [ -n "$n8n_url" ]; then
    sed -i.tmp "s|https://your-n8n.com/webhook/endpoint|$n8n_url|" .env
    rm .env.tmp 2>/dev/null || true
    echo -e "${GREEN}   ✅ n8n URL сохранен${NC}"
else
    echo -e "${YELLOW}   ⚠️  n8n URL пропущен (можно добавить позже)${NC}"
fi

# Опциональные параметры
echo ""
echo -e "${BLUE}📋 Опциональные параметры (можно пропустить):${NC}"

# Админский токен
echo ""
echo -e "${YELLOW}5. Админский токен бота (опционально):${NC}"
echo "   Для уведомлений админа. Создайте второго бота у @BotFather"
echo -n "   Введите токен (или Enter для пропуска): "
read -r admin_token

if [ -n "$admin_token" ]; then
    sed -i.tmp "s/your_admin_bot_token_here/$admin_token/" .env
    rm .env.tmp 2>/dev/null || true
    echo -e "${GREEN}   ✅ Админский токен сохранен${NC}"
    
    # Chat ID админа
    echo ""
    echo -e "${YELLOW}6. Chat ID админа:${NC}"
    echo "   Получите у @userinfobot"
    echo -n "   Введите Chat ID: "
    read -r admin_chat_id
    
    if [ -n "$admin_chat_id" ]; then
        sed -i.tmp "s/your_admin_chat_id_here/$admin_chat_id/" .env
        rm .env.tmp 2>/dev/null || true
        echo -e "${GREEN}   ✅ Chat ID сохранен${NC}"
    fi
else
    echo -e "${YELLOW}   ⚠️  Админские уведомления отключены${NC}"
fi

# Устанавливаем LOG_LEVEL в INFO
sed -i.tmp "s/LOG_LEVEL=DEBUG/LOG_LEVEL=INFO/" .env
rm .env.tmp 2>/dev/null || true

echo ""
echo -e "${GREEN}🎉 Файл .env настроен!${NC}"
echo ""
echo -e "${BLUE}🔍 Проверим конфигурацию:${NC}"
./check-network.sh

echo ""
echo -e "${BLUE}🚀 Следующие шаги:${NC}"
echo "1. Если все токены работают, запустите: ./start.sh"
echo "2. Проверьте статус: ./status.sh"
echo "3. При необходимости отредактируйте .env вручную: nano .env"
