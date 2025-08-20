# 🐳 Развертывание Telegram бота в Docker

Данное руководство поможет вам развернуть Telegram бота в Docker контейнере на любом сервере.

## 📋 Содержание

- [Системные требования](#системные-требования)
- [Быстрый старт](#быстрый-старт)
- [Подробная настройка](#подробная-настройка)
- [Управление ботом](#управление-ботом)
- [Мониторинг и логи](#мониторинг-и-логи)
- [Troubleshooting](#troubleshooting)
- [Обновление](#обновление)

## 🔧 Системные требования

### Минимальные требования:
- **OS**: Linux (Ubuntu 20.04+, CentOS 7+, Debian 10+) или macOS
- **RAM**: 512 MB
- **Storage**: 2 GB свободного места
- **Docker**: версия 20.10+
- **Docker Compose**: версия 1.29+ или Docker Compose v2

### Рекомендуемые требования:
- **RAM**: 1 GB+
- **Storage**: 5 GB+
- Стабильное интернет-соединение

## 🚀 Быстрый старт

### 1. Установка Docker (если не установлен)

#### Ubuntu/Debian:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### CentOS/RHEL:
```bash
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

#### macOS:
Скачайте Docker Desktop с [официального сайта](https://www.docker.com/products/docker-desktop/).

### 2. Клонирование и настройка

```bash
# Перейдите в директорию с ботом
cd /path/to/bot

# Скопируйте и заполните конфигурацию
cp env.example .env
nano .env  # или любой другой редактор
```

### 3. Запуск бота

```bash
./start.sh
```

Готово! Бот запущен и работает. 🎉

## ⚙️ Подробная настройка

### Настройка переменных окружения (.env)

Обязательные параметры:
```env
# Токен бота от @BotFather
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Настройки Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# URL webhook для n8n
N8N_WEBHOOK_URL=https://your-n8n.com/webhook/endpoint
```

Опциональные параметры:
```env
# Бот для уведомлений админа
ADMIN_BOT_TOKEN=admin_bot_token
ADMIN_CHAT_ID=your_admin_chat_id

# Уровень логирования
LOG_LEVEL=INFO
```

### Структура файлов

```
bot with button/
├── 🐳 Docker файлы
│   ├── Dockerfile              # Образ контейнера
│   ├── docker-compose.yml      # Конфигурация сервисов  
│   └── .dockerignore          # Исключения при сборке
├── 📁 Код бота
│   ├── main.py                # Точка входа
│   ├── bot.py                 # Основная логика бота
│   ├── config.py              # Конфигурация
│   └── ...                    # Остальные модули
├── ⚙️ Настройки
│   ├── .env                   # Переменные окружения
│   ├── env.example            # Шаблон настроек
│   └── requirements.txt       # Python зависимости
└── 🔧 Скрипты управления
    ├── start.sh               # Запуск бота
    ├── stop.sh                # Остановка бота
    ├── restart.sh             # Перезапуск бота
    └── logs.sh                # Просмотр логов
```

## 🎮 Управление ботом

### Основные команды

```bash
# Запуск бота
./start.sh

# Остановка бота
./stop.sh

# Перезапуск бота
./restart.sh

# Просмотр логов (интерактивно)
./logs.sh

# Проверка статуса
docker-compose ps
```

### Ручное управление через Docker Compose

```bash
# Запуск в фоновом режиме
docker-compose up -d

# Остановка
docker-compose down

# Просмотр логов
docker-compose logs -f telegram-bot

# Пересборка образа
docker-compose build --no-cache

# Просмотр статуса
docker-compose ps
```

## 📊 Мониторинг и логи

### Просмотр логов

Скрипт `./logs.sh` предоставляет интерактивный интерфейс для работы с логами:

1. **Последние 50/100 строк** - быстрый просмотр недавних событий
2. **Логи в реальном времени** - для отслеживания активности
3. **Поиск по ключевым словам** - для нахождения конкретных событий
4. **Фильтрация ошибок** - показывает только проблемы
5. **Экспорт в файл** - для анализа или отправки разработчикам

### Системная информация

```bash
# Использование ресурсов контейнером
docker stats telegram-bot

# Использование диска Docker
docker system df

# Информация о контейнере
docker inspect telegram-bot

# Процессы в контейнере
docker-compose exec telegram-bot ps aux
```

### Настройка ротации логов

Логи автоматически ротируются (настроено в `docker-compose.yml`):
- Максимальный размер файла: 10MB
- Количество файлов: 3
- Общий объем логов: ~30MB

## 🐛 Troubleshooting

### Частые проблемы

#### 1. Бот не запускается

**Симптомы**: Контейнер останавливается сразу после запуска
**Решение**:
```bash
# Проверьте логи
./logs.sh

# Проверьте конфигурацию
cat .env

# Убедитесь, что все обязательные параметры заполнены
grep -E "(TELEGRAM_BOT_TOKEN|SUPABASE_URL|SUPABASE_KEY)" .env
```

#### 2. Ошибки подключения к Supabase

**Симптомы**: `Connection error` в логах
**Решение**:
- Проверьте правильность `SUPABASE_URL` и `SUPABASE_KEY`
- Убедитесь, что сервер имеет доступ к интернету
- Проверьте настройки файрвола

#### 3. Webhook не работает

**Симптомы**: Бот не получает сообщения
**Решение**:
```bash
# Проверьте, что порт 8080 доступен
netstat -tlnp | grep 8080

# Проверьте webhook URL в настройках бота
curl -X GET "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"

# Установите webhook
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
     -d "url=https://your-domain.com:8080/webhook"
```

#### 4. Проблемы с правами доступа

**Симптомы**: `Permission denied` ошибки
**Решение**:
```bash
# Добавьте пользователя в группу docker
sudo usermod -aG docker $USER

# Перелогиньтесь или выполните
newgrp docker

# Проверьте права на файлы
ls -la *.sh
chmod +x *.sh  # если нужно
```

### Диагностические команды

```bash
# Проверка Docker
docker --version
docker-compose --version

# Проверка сетевой доступности
docker run --rm busybox ping -c 3 google.com

# Проверка образов
docker images | grep telegram

# Очистка Docker (если нужно место)
docker system prune -a
```

## 🔄 Обновление

### Обновление кода бота

```bash
# Остановите бота
./stop.sh

# Обновите код (git pull, или скопируйте новые файлы)
git pull origin main  # если используете git

# Перезапустите с пересборкой
./restart.sh
```

### Обновление Docker образов

```bash
# Обновление базового Python образа
docker-compose build --no-cache

# Принудительное обновление
docker-compose down --rmi all
docker-compose build
docker-compose up -d
```

## 🔒 Безопасность

### Рекомендации по безопасности

1. **Не добавляйте .env в git**:
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Используйте сильные токены**: Регулярно меняйте токены ботов

3. **Ограничьте доступ к серверу**: Используйте файрвол и SSH ключи

4. **Мониторинг**: Регулярно проверяйте логи на подозрительную активность

5. **Обновления**: Регулярно обновляйте Docker и зависимости

### Настройка HTTPS (рекомендуется)

Для продакшена рекомендуется использовать HTTPS с реверс-прокси (nginx):

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте [Troubleshooting](#troubleshooting)
2. Изучите логи с помощью `./logs.sh`
3. Проверьте конфигурацию в `.env`
4. Обратитесь к разработчику с логами и описанием проблемы

## 📝 Дополнительные ресурсы

- [Документация Docker](https://docs.docker.com/)
- [Документация Docker Compose](https://docs.docker.com/compose/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Supabase Documentation](https://supabase.com/docs)

---

🎉 **Поздравляем!** Ваш Telegram бот успешно развернут в Docker. Удачного использования!
