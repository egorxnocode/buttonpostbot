#!/bin/bash

# Скрипт для остановки Telegram бота

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🛑 Остановка Telegram бота...${NC}"
echo ""

# Проверяем, что Docker Compose доступен
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose не установлен!${NC}"
    exit 1
fi

# Проверяем, запущен ли контейнер
if ! docker-compose ps | grep -q "telegram-bot"; then
    echo -e "${YELLOW}⚠️  Контейнер telegram-bot не найден или уже остановлен${NC}"
else
    # Показываем текущий статус
    echo -e "${BLUE}📊 Текущий статус контейнера:${NC}"
    docker-compose ps
    echo ""
    
    # Останавливаем контейнер
    echo -e "${YELLOW}🛑 Остановка контейнера...${NC}"
    docker-compose down
    
    echo -e "${GREEN}✅ Бот успешно остановлен!${NC}"
fi

# Функция для показа дополнительных опций
show_cleanup_options() {
    echo ""
    echo -e "${BLUE}🧹 Дополнительные опции очистки:${NC}"
    echo "1) Удалить только контейнер (сохранить образ)"
    echo "2) Удалить контейнер и образ"
    echo "3) Удалить всё (контейнер, образ, volume)"
    echo "4) Показать использование дискового пространства Docker"
    echo "0) Пропустить очистку"
    echo ""
    echo -n "Ваш выбор: "
}

# Предлагаем дополнительную очистку
show_cleanup_options
read -r choice

case $choice in
    1)
        echo -e "${YELLOW}🗑️  Удаление контейнера...${NC}"
        docker-compose rm -f 2>/dev/null || true
        echo -e "${GREEN}✅ Контейнер удален${NC}"
        ;;
    2)
        echo -e "${YELLOW}🗑️  Удаление контейнера и образа...${NC}"
        docker-compose rm -f 2>/dev/null || true
        docker-compose down --rmi all 2>/dev/null || true
        echo -e "${GREEN}✅ Контейнер и образ удалены${NC}"
        ;;
    3)
        echo -e "${YELLOW}🗑️  Полная очистка...${NC}"
        docker-compose down --rmi all --volumes --remove-orphans 2>/dev/null || true
        echo -e "${GREEN}✅ Полная очистка выполнена${NC}"
        ;;
    4)
        echo -e "${BLUE}💾 Использование дискового пространства Docker:${NC}"
        docker system df
        echo ""
        echo -e "${YELLOW}Для очистки неиспользуемых данных Docker выполните:${NC}"
        echo "docker system prune"
        ;;
    0|*)
        echo -e "${GREEN}✅ Очистка пропущена${NC}"
        ;;
esac

echo ""
echo -e "${BLUE}🔍 Полезные команды:${NC}"
echo -e "  ${YELLOW}Запуск бота:${NC} ./start.sh"
echo -e "  ${YELLOW}Просмотр логов:${NC} ./logs.sh"
echo -e "  ${YELLOW}Статус контейнеров:${NC} docker-compose ps"
echo -e "  ${YELLOW}Перезапуск:${NC} ./restart.sh"
echo ""
echo -e "${GREEN}👋 Бот остановлен. До свидания!${NC}"
