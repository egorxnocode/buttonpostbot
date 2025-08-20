# 🚀 Быстрый запуск бота в Docker

## 📋 Что нужно сделать:

### 1. Установить Docker (если не установлен)
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Перелогиниться или выполнить
newgrp docker
```

### 2. Настроить переменные окружения
```bash
# Скопировать шаблон
cp env.example .env

# Отредактировать файл .env
nano .env
```

**Обязательно заполните:**
- `TELEGRAM_BOT_TOKEN` - токен от @BotFather
- `SUPABASE_URL` - URL вашего Supabase проекта  
- `SUPABASE_KEY` - ключ Supabase
- `N8N_WEBHOOK_URL` - URL webhook n8n

### 3. Запустить бота
```bash
./start.sh
```

## 🎮 Управление ботом

| Команда | Описание |
|---------|----------|
| `./start.sh` | Запуск бота |
| `./stop.sh` | Остановка бота |
| `./restart.sh` | Перезапуск бота |
| `./logs.sh` | Просмотр логов (интерактивно) |
| `./status.sh` | Проверка статуса |

## 🔍 Проверка работы

После запуска:
1. Выполните `./status.sh` - должно показать статус "Запущен"
2. Откройте http://localhost:8080/health - должно вернуть `{"status":"ok"}`
3. Проверьте логи: `./logs.sh`

## 🆘 Если что-то не работает

1. Проверьте логи: `./logs.sh`
2. Убедитесь, что все переменные в `.env` заполнены
3. Проверьте, что Docker запущен: `docker --version`
4. Почитайте подробное руководство: `DOCKER_DEPLOYMENT.md`

## 📞 Полезные ссылки

- [Подробное руководство](DOCKER_DEPLOYMENT.md)
- [Настройка n8n](N8N_SETUP.md)
- [Примеры использования](USAGE_EXAMPLE.md)

---

**Готово!** 🎉 Ваш бот работает в Docker!
