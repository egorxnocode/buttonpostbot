#!/bin/bash

# Скрипт для запуска Telegram бота в Docker

set -e  # Останавливаться при ошибках

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Логотип
echo -e "${BLUE}"
echo "████████╗███████╗██╗     ███████╗ ██████╗ ██████╗  █████╗ ███╗   ███╗"
echo "╚══██╔══╝██╔════╝██║     ██╔════╝██╔════╝ ██╔══██╗██╔══██╗████╗ ████║"
echo "   ██║   █████╗  ██║     █████╗  ██║  ███╗██████╔╝███████║██╔████╔██║"
echo "   ██║   ██╔══╝  ██║     ██╔══╝  ██║   ██║██╔══██╗██╔══██║██║╚██╔╝██║"
echo "   ██║   ███████╗███████╗███████╗╚██████╔╝██║  ██║██║  ██║██║ ╚═╝ ██║"
echo "   ╚═╝   ╚══════╝╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝"
echo "                               ██████╗  ██████╗ ████████╗"
echo "                               ██╔══██╗██╔═══██╗╚══██╔══╝"
echo "                               ██████╔╝██║   ██║   ██║"
echo "                               ██╔══██╗██║   ██║   ██║"
echo "                               ██████╔╝╚██████╔╝   ██║"
echo "                               ╚═════╝  ╚═════╝    ╚═╝"
echo -e "${NC}"

echo -e "${GREEN}🚀 Запуск Telegram бота в Docker...${NC}"

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Файл .env не найден!${NC}"
    echo -e "${YELLOW}📝 Скопируйте env.example в .env и заполните его:${NC}"
    echo "cp env.example .env"
    echo "nano .env"
    exit 1
fi

# Проверяем, что Docker установлен
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker не установлен!${NC}"
    echo -e "${YELLOW}📦 Установите Docker: https://docs.docker.com/get-docker/${NC}"
    exit 1
fi

# Проверяем, что Docker Compose установлен
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose не установлен!${NC}"
    echo -e "${YELLOW}📦 Установите Docker Compose: https://docs.docker.com/compose/install/${NC}"
    exit 1
fi

# Создаем директорию для логов
mkdir -p logs

# Останавливаем контейнер, если он уже запущен
echo -e "${YELLOW}🛑 Остановка существующих контейнеров...${NC}"
docker-compose down 2>/dev/null || true

# Собираем образ
echo -e "${BLUE}🔨 Сборка Docker образа...${NC}"
docker-compose build

# Запускаем контейнер
echo -e "${GREEN}🚀 Запуск контейнера...${NC}"
docker-compose up -d

# Проверяем статус
sleep 3
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Бот успешно запущен!${NC}"
    echo ""
    echo -e "${BLUE}📊 Информация о контейнере:${NC}"
    docker-compose ps
    echo ""
    echo -e "${BLUE}🔍 Полезные команды:${NC}"
    echo -e "  ${YELLOW}Просмотр логов:${NC} ./logs.sh"
    echo -e "  ${YELLOW}Остановка бота:${NC} ./stop.sh"
    echo -e "  ${YELLOW}Перезапуск:${NC} ./restart.sh"
    echo -e "  ${YELLOW}Статус:${NC} docker-compose ps"
    echo ""
    echo -e "${GREEN}🎉 Бот готов к работе!${NC}"
    echo -e "${BLUE}📱 Webhook доступен на: http://localhost:8080${NC}"
else
    echo -e "${RED}❌ Ошибка при запуске бота!${NC}"
    echo -e "${YELLOW}📋 Логи контейнера:${NC}"
    docker-compose logs
    exit 1
fi
