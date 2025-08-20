#!/bin/bash

# Скрипт для просмотра логов Telegram бота

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 Просмотр логов Telegram бота${NC}"
echo ""

# Проверяем, что контейнер запущен
if ! docker-compose ps | grep -q "telegram-bot"; then
    echo -e "${RED}❌ Контейнер telegram-bot не найден!${NC}"
    echo -e "${YELLOW}🚀 Запустите бота сначала: ./start.sh${NC}"
    exit 1
fi

# Проверяем статус контейнера
container_status=$(docker-compose ps | grep telegram-bot | grep -o 'Up\|Restarting\|Exited' | head -1 || echo "NotFound")

if [ "$container_status" = "NotFound" ]; then
    echo -e "${RED}❌ Контейнер telegram-bot не найден!${NC}"
    echo -e "${YELLOW}🚀 Запустите бота: ./start.sh${NC}"
    exit 1
elif [ "$container_status" = "Restarting" ]; then
    echo -e "${YELLOW}⚠️  Контейнер перезапускается (возможна ошибка)${NC}"
    echo -e "${BLUE}🔍 Для диагностики используйте: ./debug.sh${NC}"
    echo ""
elif [ "$container_status" = "Exited" ]; then
    echo -e "${RED}❌ Контейнер остановлен!${NC}"
    echo -e "${YELLOW}🚀 Запустите бота: ./start.sh${NC}"
    exit 1
fi

# Функция для показа меню
show_menu() {
    echo -e "${BLUE}Выберите действие:${NC}"
    echo "1) Показать последние 50 строк логов"
    echo "2) Показать последние 100 строк логов"
    echo "3) Показать логи в реальном времени (следить за логами)"
    echo "4) Показать все логи"
    echo "5) Поиск в логах по ключевому слову"
    echo "6) Показать логи за последний час"
    echo "7) Показать только ошибки"
    echo "8) Экспорт логов в файл"
    echo "0) Выход"
    echo ""
    echo -n "Ваш выбор: "
}

# Основной цикл
while true; do
    show_menu
    read -r choice
    
    case $choice in
        1)
            echo -e "${GREEN}📋 Последние 50 строк логов:${NC}"
            docker-compose logs --tail=50 telegram-bot
            echo ""
            ;;
        2)
            echo -e "${GREEN}📋 Последние 100 строк логов:${NC}"
            docker-compose logs --tail=100 telegram-bot
            echo ""
            ;;
        3)
            echo -e "${GREEN}📋 Логи в реальном времени (Ctrl+C для выхода):${NC}"
            echo -e "${YELLOW}Нажмите Ctrl+C для возврата в меню${NC}"
            docker-compose logs -f telegram-bot
            echo ""
            ;;
        4)
            echo -e "${GREEN}📋 Все логи:${NC}"
            docker-compose logs telegram-bot
            echo ""
            ;;
        5)
            echo -n "Введите ключевое слово для поиска: "
            read -r keyword
            if [ -n "$keyword" ]; then
                echo -e "${GREEN}🔍 Поиск '$keyword' в логах:${NC}"
                docker-compose logs telegram-bot | grep -i "$keyword" || echo -e "${YELLOW}Ничего не найдено${NC}"
            else
                echo -e "${RED}❌ Ключевое слово не может быть пустым${NC}"
            fi
            echo ""
            ;;
        6)
            echo -e "${GREEN}📋 Логи за последний час:${NC}"
            docker-compose logs --since=1h telegram-bot
            echo ""
            ;;
        7)
            echo -e "${GREEN}❌ Только ошибки:${NC}"
            docker-compose logs telegram-bot | grep -i "error\|exception\|traceback\|critical" || echo -e "${YELLOW}Ошибок не найдено${NC}"
            echo ""
            ;;
        8)
            timestamp=$(date +"%Y%m%d_%H%M%S")
            filename="telegram_bot_logs_${timestamp}.log"
            echo -e "${GREEN}💾 Экспорт логов в файл ${filename}...${NC}"
            docker-compose logs telegram-bot > "$filename"
            echo -e "${GREEN}✅ Логи сохранены в файл: ${filename}${NC}"
            echo ""
            ;;
        0)
            echo -e "${GREEN}👋 До свидания!${NC}"
            break
            ;;
        *)
            echo -e "${RED}❌ Неверный выбор. Попробуйте снова.${NC}"
            echo ""
            ;;
    esac
    
    # Пауза перед показом меню снова (кроме случая выхода)
    if [ "$choice" != "0" ] && [ "$choice" != "3" ]; then
        echo -e "${YELLOW}Нажмите Enter для продолжения...${NC}"
        read -r
        clear
    fi
done
