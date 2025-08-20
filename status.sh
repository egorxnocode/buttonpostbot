#!/bin/bash

# Скрипт для проверки статуса Telegram бота

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Функция для проверки health check
check_health() {
    local url="http://localhost:8080/health"
    local response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$url" 2>/dev/null || echo "HTTPSTATUS:000")
    local body=$(echo "$response" | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
    local status=$(echo "$response" | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')
    
    if [ "$status" -eq 200 ]; then
        echo -e "${GREEN}✅ Health check: OK${NC}"
        return 0
    else
        echo -e "${RED}❌ Health check: FAILED (HTTP $status)${NC}"
        return 1
    fi
}

# Функция для проверки памяти контейнера
check_memory() {
    local stats=$(docker stats telegram-bot --no-stream --format "table {{.MemUsage}}\t{{.MemPerc}}" 2>/dev/null | tail -n 1)
    if [ -n "$stats" ]; then
        echo -e "${CYAN}💾 Memory: $stats${NC}"
    else
        echo -e "${RED}❌ Не удалось получить статистику памяти${NC}"
    fi
}

# Функция для проверки CPU
check_cpu() {
    local cpu=$(docker stats telegram-bot --no-stream --format "table {{.CPUPerc}}" 2>/dev/null | tail -n 1)
    if [ -n "$cpu" ]; then
        echo -e "${CYAN}⚡ CPU: $cpu${NC}"
    else
        echo -e "${RED}❌ Не удалось получить статистику CPU${NC}"
    fi
}

# Функция для проверки uptime
check_uptime() {
    local started=$(docker inspect telegram-bot --format='{{.State.StartedAt}}' 2>/dev/null)
    if [ -n "$started" ]; then
        local started_unix=$(date -d "$started" +%s 2>/dev/null || date -jf "%Y-%m-%dT%H:%M:%S" "$started" +%s 2>/dev/null)
        local current_unix=$(date +%s)
        local uptime_seconds=$((current_unix - started_unix))
        local uptime_human=$(printf '%dd %dh %dm %ds' $((uptime_seconds/86400)) $((uptime_seconds%86400/3600)) $((uptime_seconds%3600/60)) $((uptime_seconds%60)))
        echo -e "${PURPLE}⏰ Uptime: $uptime_human${NC}"
    else
        echo -e "${RED}❌ Не удалось получить время запуска${NC}"
    fi
}

# Функция для проверки последних логов
check_recent_logs() {
    echo -e "${BLUE}📋 Последние 5 строк логов:${NC}"
    docker-compose logs --tail=5 telegram-bot 2>/dev/null | sed 's/^/  /' || echo -e "${RED}  ❌ Не удалось получить логи${NC}"
}

# Заголовок
echo -e "${BLUE}"
echo "███████╗████████╗ █████╗ ████████╗██╗   ██╗███████╗"
echo "██╔════╝╚══██╔══╝██╔══██╗╚══██╔══╝██║   ██║██╔════╝"
echo "███████╗   ██║   ███████║   ██║   ██║   ██║███████╗"
echo "╚════██║   ██║   ██╔══██║   ██║   ██║   ██║╚════██║"
echo "███████║   ██║   ██║  ██║   ██║   ╚██████╔╝███████║"
echo "╚══════╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚══════╝"
echo -e "${NC}"

echo -e "${BLUE}🤖 Статус Telegram бота${NC}"
echo "================================"

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker не установлен!${NC}"
    exit 1
fi

# Проверяем наличие docker-compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose не установлен!${NC}"
    exit 1
fi

# Проверяем существование контейнера
if ! docker ps -a --format "table {{.Names}}" | grep -q "telegram-bot"; then
    echo -e "${RED}❌ Контейнер telegram-bot не найден!${NC}"
    echo -e "${YELLOW}🚀 Запустите бота: ./start.sh${NC}"
    exit 1
fi

# Основная информация о контейнере
echo -e "${BLUE}📊 Информация о контейнере:${NC}"
container_status=$(docker inspect telegram-bot --format='{{.State.Status}}' 2>/dev/null)

case $container_status in
    "running")
        echo -e "${GREEN}✅ Статус: Запущен${NC}"
        ;;
    "exited")
        echo -e "${RED}❌ Статус: Остановлен${NC}"
        exit_code=$(docker inspect telegram-bot --format='{{.State.ExitCode}}' 2>/dev/null)
        echo -e "${RED}   Exit code: $exit_code${NC}"
        echo -e "${YELLOW}🚀 Запустите бота: ./start.sh${NC}"
        exit 1
        ;;
    "restarting")
        echo -e "${YELLOW}🔄 Статус: Перезапускается${NC}"
        ;;
    *)
        echo -e "${RED}❌ Статус: $container_status${NC}"
        exit 1
        ;;
esac

# Детальная информация (только если контейнер запущен)
if [ "$container_status" = "running" ]; then
    echo ""
    echo -e "${BLUE}🔍 Детальная информация:${NC}"
    
    # Проверяем health check
    check_health
    
    # Проверяем ресурсы
    check_memory
    check_cpu
    check_uptime
    
    echo ""
    
    # Последние логи
    check_recent_logs
    
    echo ""
    echo -e "${BLUE}🌐 Сетевая информация:${NC}"
    echo -e "${CYAN}📡 Webhook URL: http://localhost:8080${NC}"
    echo -e "${CYAN}🔗 Health check: http://localhost:8080/health${NC}"
    
    # Проверяем открытые порты
    if command -v netstat &> /dev/null; then
        if netstat -tlnp 2>/dev/null | grep -q ":8080"; then
            echo -e "${GREEN}✅ Порт 8080: Открыт${NC}"
        else
            echo -e "${RED}❌ Порт 8080: Закрыт${NC}"
        fi
    fi
fi

echo ""
echo -e "${BLUE}🔧 Управление ботом:${NC}"
echo -e "  ${YELLOW}Просмотр логов:${NC} ./logs.sh"
echo -e "  ${YELLOW}Остановка бота:${NC} ./stop.sh"
echo -e "  ${YELLOW}Перезапуск бота:${NC} ./restart.sh"
echo -e "  ${YELLOW}Обновление статуса:${NC} ./status.sh"

echo ""
echo -e "${GREEN}✨ Проверка завершена!${NC}"
