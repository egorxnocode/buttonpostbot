#!/bin/bash

# Скрипт для диагностики проблем с ботом

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Диагностика Telegram бота${NC}"
echo "================================"

# Проверяем статус контейнера
echo -e "${BLUE}📊 Статус контейнера:${NC}"
docker-compose ps

echo ""
echo -e "${BLUE}📋 Последние 20 строк логов:${NC}"
docker-compose logs --tail=20 telegram-bot

echo ""
echo -e "${BLUE}🔍 Инспекция контейнера:${NC}"
docker inspect telegram-bot --format='{{.State.Status}}: {{.State.Error}}'

echo ""
echo -e "${BLUE}⚠️  Ошибки из логов:${NC}"
docker-compose logs telegram-bot | grep -i "error\|exception\|traceback\|critical" | tail -10 || echo "Ошибок не найдено"

echo ""
echo -e "${BLUE}📁 Проверка файла .env:${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ Файл .env существует${NC}"
    echo "Переменные (без значений):"
    grep -v '^#' .env | grep '=' | cut -d'=' -f1 | sed 's/^/  - /'
    echo ""
    echo "Проверим обязательные переменные:"
    for var in TELEGRAM_BOT_TOKEN SUPABASE_URL SUPABASE_KEY; do
        if grep -q "^${var}=" .env && [ -n "$(grep "^${var}=" .env | cut -d'=' -f2)" ]; then
            echo -e "  ${GREEN}✅ ${var}: заполнено${NC}"
        else
            echo -e "  ${RED}❌ ${var}: пустое или отсутствует${NC}"
        fi
    done
else
    echo -e "${RED}❌ Файл .env не найден!${NC}"
    echo "Создайте его: cp env.example .env"
fi

echo ""
echo -e "${BLUE}🌐 Проверка сети:${NC}"
docker run --rm --network container:telegram-bot busybox ping -c 2 8.8.8.8 2>/dev/null && echo -e "${GREEN}✅ Интернет доступен${NC}" || echo -e "${RED}❌ Проблемы с интернетом${NC}"

echo ""
echo -e "${BLUE}💾 Использование ресурсов:${NC}"
docker stats telegram-bot --no-stream 2>/dev/null || echo "Контейнер не запущен"

echo ""
echo -e "${BLUE}🔧 Рекомендации:${NC}"
if docker-compose logs telegram-bot | grep -q "TELEGRAM_BOT_TOKEN"; then
    echo -e "${YELLOW}1. Проверьте токен бота в .env${NC}"
fi
if docker-compose logs telegram-bot | grep -q "SUPABASE"; then
    echo -e "${YELLOW}2. Проверьте настройки Supabase в .env${NC}"
fi
if docker-compose logs telegram-bot | grep -q "Connection"; then
    echo -e "${YELLOW}3. Проверьте интернет соединение${NC}"
fi
echo -e "${YELLOW}4. Для полных логов: docker-compose logs -f telegram-bot${NC}"
echo -e "${YELLOW}5. Для перезапуска: ./restart.sh${NC}"
