#!/bin/bash

# Скрипт для перезапуска Telegram бота

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 Перезапуск Telegram бота...${NC}"
echo ""

# Проверяем, что Docker Compose доступен
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose не установлен!${NC}"
    exit 1
fi

# Останавливаем контейнер
echo -e "${YELLOW}🛑 Остановка текущего контейнера...${NC}"
docker-compose down 2>/dev/null || true

# Пересобираем образ
echo -e "${BLUE}🔨 Пересборка образа...${NC}"
docker-compose build

# Запускаем заново
echo -e "${GREEN}🚀 Запуск контейнера...${NC}"
docker-compose up -d

# Проверяем статус
sleep 3
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Бот успешно перезапущен!${NC}"
    echo ""
    echo -e "${BLUE}📊 Статус контейнера:${NC}"
    docker-compose ps
    echo ""
    echo -e "${BLUE}🔍 Полезные команды:${NC}"
    echo -e "  ${YELLOW}Просмотр логов:${NC} ./logs.sh"
    echo -e "  ${YELLOW}Остановка бота:${NC} ./stop.sh"
    echo -e "  ${YELLOW}Статус:${NC} docker-compose ps"
    echo ""
    echo -e "${GREEN}🎉 Бот готов к работе!${NC}"
else
    echo -e "${RED}❌ Ошибка при перезапуске бота!${NC}"
    echo -e "${YELLOW}📋 Логи контейнера:${NC}"
    docker-compose logs
    exit 1
fi
