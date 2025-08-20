# 🐙 Развертывание бота через Git

Быстрое развертывание Telegram бота на сервере через GitHub репозиторий [egorxnocode/buttonpostbot](https://github.com/egorxnocode/buttonpostbot).

## 🚀 Установка на сервер в 4 команды

### 📋 Предварительные требования
- Сервер с установленным Docker и Docker Compose
- Доступ к серверу по SSH
- Git установлен на сервере

### ⚡ Быстрая установка

```bash
# 1. Клонируем репозиторий
git clone https://github.com/egorxnocode/buttonpostbot.git
cd buttonpostbot

# 2. Настраиваем переменные окружения
cp env.example .env
nano .env  # или vim .env

# 3. Запускаем бота
./start.sh

# 4. Проверяем статус
./status.sh
```

**Готово!** 🎉 Бот запущен и работает.

## 📝 Детальная инструкция

### 🔧 Шаг 1: Подключение к серверу
```bash
ssh username@your-server-ip
```

### 📦 Шаг 2: Клонирование репозитория
```bash
# Клонировать в домашнюю директорию
cd ~
git clone https://github.com/egorxnocode/buttonpostbot.git

# Перейти в папку проекта
cd buttonpostbot

# Проверить, что все файлы загружены
ls -la
```

### ⚙️ Шаг 3: Настройка конфигурации
```bash
# Скопировать шаблон настроек
cp env.example .env

# Открыть редактор для заполнения
nano .env
```

**Обязательно заполните в .env:**
```env
# Токен бота от @BotFather
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Настройки Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# URL webhook для n8n
N8N_WEBHOOK_URL=https://your-n8n.com/webhook/endpoint

# Опционально: админский бот
ADMIN_BOT_TOKEN=admin_bot_token
ADMIN_CHAT_ID=your_admin_chat_id

# Уровень логирования
LOG_LEVEL=INFO
```

### 🚀 Шаг 4: Запуск бота
```bash
# Проверить права на выполнение скриптов
chmod +x *.sh

# Запустить бота
./start.sh
```

Скрипт автоматически:
- ✅ Проверит наличие Docker
- ✅ Создаст директорию для логов
- ✅ Соберет Docker образ
- ✅ Запустит контейнер
- ✅ Покажет статус

### ✅ Шаг 5: Проверка работы
```bash
# Полная диагностика системы
./status.sh

# Просмотр логов (интерактивно)
./logs.sh

# Быстрая проверка health check
curl http://localhost:8080/health
```

## 🎮 Команды управления

| Команда | Описание |
|---------|----------|
| `./start.sh` | Запуск бота с проверками |
| `./stop.sh` | Остановка бота + опции очистки |
| `./restart.sh` | Перезапуск с пересборкой |
| `./logs.sh` | Интерактивный просмотр логов |
| `./status.sh` | Мониторинг состояния |
| `git pull` | Обновление кода |

## 🔄 Обновление бота

Когда выйдет новая версия:

```bash
# Остановить бота
./stop.sh

# Получить обновления
git pull origin main

# Перезапустить с новой версией
./restart.sh

# Проверить, что все работает
./status.sh
```

## 🌐 Настройка для внешнего доступа

### Вариант 1: Прямое подключение
Если у сервера есть внешний IP, измените в `docker-compose.yml`:
```yaml
ports:
  - "0.0.0.0:8080:8080"  # вместо "8080:8080"
```

### Вариант 2: Через nginx (рекомендуется)
```bash
# Установить nginx
sudo apt update && sudo apt install nginx

# Настроить прокси
sudo nano /etc/nginx/sites-available/telegram-bot
```

Конфигурация nginx:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Активировать сайт:
```bash
sudo ln -s /etc/nginx/sites-available/telegram-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔒 Безопасность

### Настройка SSH (рекомендуется)
```bash
# Создать SSH ключ (локально)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Скопировать ключ на сервер
ssh-copy-id username@your-server-ip

# Отключить парольную аутентификацию
sudo nano /etc/ssh/sshd_config
# Установить: PasswordAuthentication no
sudo systemctl restart ssh
```

### Настройка firewall
```bash
# Разрешить только нужные порты
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

## 🚨 Устранение проблем

### Docker не установлен
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### Ошибки с правами
```bash
sudo usermod -aG docker $USER
newgrp docker
chmod +x *.sh
```

### Порт занят
```bash
# Найти процесс
sudo netstat -tlnp | grep 8080

# Остановить процесс или изменить порт в docker-compose.yml
```

### Git ошибки
```bash
# Переклонировать репозиторий
rm -rf buttonpostbot
git clone https://github.com/egorxnocode/buttonpostbot.git
```

## 📊 Мониторинг в продакшене

### Автозапуск при перезагрузке сервера
```bash
# Создать systemd сервис
sudo nano /etc/systemd/system/telegram-bot.service
```

Содержимое сервиса:
```ini
[Unit]
Description=Telegram Bot
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory=/home/username/buttonpostbot
ExecStart=/home/username/buttonpostbot/start.sh
ExecStop=/home/username/buttonpostbot/stop.sh
User=username

[Install]
WantedBy=multi-user.target
```

Активировать:
```bash
sudo systemctl enable telegram-bot.service
sudo systemctl start telegram-bot.service
```

### Мониторинг ресурсов
```bash
# Использование ресурсов ботом
docker stats telegram-bot

# Логи системы
journalctl -u telegram-bot.service -f

# Дисковое пространство
df -h
docker system df
```

## 🎯 Готовые команды для копирования

### Полная установка одной командой
```bash
git clone https://github.com/egorxnocode/buttonpostbot.git && cd buttonpostbot && cp env.example .env && echo "Теперь отредактируйте .env и запустите ./start.sh"
```

### Быстрое обновление
```bash
./stop.sh && git pull && ./restart.sh && ./status.sh
```

### Полная переустановка
```bash
./stop.sh && cd .. && rm -rf buttonpostbot && git clone https://github.com/egorxnocode/buttonpostbot.git && cd buttonpostbot
```

---

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи: `./logs.sh`
2. Проверьте статус: `./status.sh`
3. Обратитесь к [issues в репозитории](https://github.com/egorxnocode/buttonpostbot/issues)

**🎉 Готово!** Ваш бот развернут через Git и готов к работе!
