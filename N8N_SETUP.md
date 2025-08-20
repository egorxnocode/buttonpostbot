# Настройка n8n для интеграции с Telegram ботом

## Создание Workflow в n8n

### 1. Webhook Node (входящий)
- **URL**: `https://your-n8n-instance.com/webhook/generate-post`
- **HTTP Method**: POST
- **Response Mode**: Respond to Webhook

### 2. Обработка данных
Входящие данные от бота:
```json
{
  "user": {
    "telegram_id": 123456789,
    "email": "user@example.com", 
    "channel_url": "https://t.me/channel",
    "first_name": "John",
    "last_name": "Doe"
  },
  "answers": {
    "topic": "Новый продукт",
    "goal": "Купить товар", 
    "additional_info": "Скидка 20%, до конца месяца"
  },
  "request_type": "generate_post",
  "timestamp": 1234567890.123
}
```

### 3. AI Node (генерация поста)
Используйте один из AI узлов (OpenAI, Claude, etc.) с промптом:

```
Создай пост для Telegram канала на основе следующих данных:

Тема поста: {{$json["answers"]["topic"]}}
Цель поста: {{$json["answers"]["goal"]}}
Дополнительная информация: {{$json["answers"]["additional_info"]}}

Требования к посту:
1. Используй эмодзи для привлекательности
2. Структурируй текст с переносами строк
3. Добавь призыв к действию в конце
4. Длина поста: 100-300 слов
5. Используй HTML разметку для Telegram (жирный, курсив)

Пример структуры:
🎯 [Заголовок с эмодзи]

📝 [Основной текст поста]

💡 [Дополнительная информация]

👉 [Призыв к действию]

Создай готовый пост:
```

### 4. HTTP Request Node (ответ боту)
- **Method**: POST
- **URL**: `https://your-bot-webhook-server.com/webhook/n8n`
- **Body**:
```json
{
  "telegram_id": "{{$json['user']['telegram_id']}}",
  "generated_post": "{{$json['ai_response']}}"
}
```

## Пример готового workflow

```json
{
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "generate-post",
        "responseMode": "responseNode"
      },
      "id": "webhook",
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "position": [240, 300]
    },
    {
      "parameters": {
        "model": "gpt-3.5-turbo",
        "messages": {
          "messageValues": [
            {
              "role": "user",
              "message": "=Создай пост для Telegram канала...[промпт выше]"
            }
          ]
        }
      },
      "id": "openai",
      "name": "OpenAI",
      "type": "@n8n/n8n-nodes-langchain.openAi",
      "position": [460, 300]
    },
    {
      "parameters": {
        "url": "https://your-bot-server.com/webhook/n8n",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "telegram_id",
              "value": "={{$('webhook').item.json.user.telegram_id}}"
            },
            {
              "name": "generated_post", 
              "value": "={{$('openai').item.json.response}}"
            }
          ]
        }
      },
      "id": "http_request",
      "name": "Send to Bot",
      "type": "n8n-nodes-base.httpRequest",
      "position": [680, 300]
    }
  ],
  "connections": {
    "Webhook": {
      "main": [
        [
          {
            "node": "OpenAI",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "OpenAI": {
      "main": [
        [
          {
            "node": "Send to Bot",
            "type": "main", 
            "index": 0
          }
        ]
      ]
    }
  }
}
```

## Настройка безопасности

### 1. Аутентификация
Добавьте проверку токена или подписи для защиты webhook:

```javascript
// В Code Node перед обработкой
const expectedToken = 'your-secret-token';
const receivedToken = $input.item.json.auth_token;

if (receivedToken !== expectedToken) {
  throw new Error('Unauthorized');
}
```

### 2. Rate Limiting
Ограничьте количество запросов от одного пользователя.

### 3. Validation
Проверяйте структуру входящих данных:

```javascript
const requiredFields = ['user', 'answers', 'request_type'];
const data = $input.item.json;

for (const field of requiredFields) {
  if (!data[field]) {
    throw new Error(`Missing required field: ${field}`);
  }
}
```

## Мониторинг и логирование

1. Добавьте логирование всех запросов
2. Настройте алерты при ошибках
3. Отслеживайте время ответа AI
4. Ведите статистику генераций

## Тестирование

Для тестирования workflow используйте curl:

```bash
curl -X POST https://your-n8n-instance.com/webhook/generate-post \
  -H "Content-Type: application/json" \
  -d '{
    "user": {
      "telegram_id": 123456789,
      "email": "test@example.com",
      "channel_url": "https://t.me/testchannel"
    },
    "answers": {
      "topic": "Тестовый пост",
      "goal": "Протестировать систему",
      "additional_info": "Это тест"
    },
    "request_type": "generate_post"
  }'
```

## Обработка ошибок

Добавьте обработку ошибок в workflow:

1. **Timeout Node** - для обработки долгих запросов к AI
2. **Error Trigger** - для логирования ошибок
3. **Retry Logic** - для повторных попыток при сбоях

Пример обработки ошибки:
```json
{
  "telegram_id": 123456789,
  "error": "Failed to generate post",
  "retry_count": 2
}
```
