# Формат материалов для N8N агента

## 📤 Что получает N8N агент

### Структура payload:

```json
{
  "user": {
    "telegram_id": 123456789,
    "email": "user@example.com",
    "channel_url": "https://t.me/username",
    "first_name": "Имя",
    "last_name": "Фамилия"
  },
  "answers": {
    "name_profession": "Меня зовут Анна, я диетолог",
    "target_clients": "Женщины 30+ с лишним весом",
    "results_timeline": "Помогаю похудеть на 5-7 кг за месяц",
    "main_service": "Диагностическая консультация",
    "what_exclude": "Без жестких диет и голодания"
  },
  "materials": [
    "5 секретов быстрого похудения https://t.me/channel/post123",
    "Бесплатный вебинар по питанию https://example.com/webinar",
    "Полезные рецепты для похудения https://example.com/recipes"
  ],
  "request_type": "generate_post",
  "session_id": 456,
  "timestamp": 1701234567
}
```

## 📋 Формат поля "materials"

**Тип:** Массив строк  
**Максимум:** 5 элементов  
**Формат каждого элемента:** `"Описание материала URL"`

### Примеры:

```json
"materials": [
  "Топ-10 упражнений для дома https://t.me/fitness/123",
  "Видео урок по йоге https://youtube.com/watch?v=abc123",
  "Статья о правильном питании https://myblog.com/nutrition",
  "Бесплатная консультация https://calendly.com/coach",
  "Чек-лист здорового завтрака https://drive.google.com/file/d/123"
]
```

## 🔍 Что может содержать массив:

- **0 элементов** - пользователь не добавил материалы
- **1-5 элементов** - каждый содержит описание + ссылку через пробел
- **Только заполненные** - пустые материалы отфильтрованы

## 💡 Как использовать в агенте:

### Простое чтение:
```javascript
// Получить все материалы
const materials = payload.materials;

// Количество материалов
const count = materials.length;

// Первый материал
const firstMaterial = materials[0]; // "Описание https://example.com"
```

### Парсинг описания и ссылки:
```javascript
materials.forEach(material => {
  const parts = material.split(' ');
  const url = parts[parts.length - 1]; // Последний элемент - ссылка
  const description = parts.slice(0, -1).join(' '); // Все остальное - описание
  
  console.log(`Описание: ${description}`);
  console.log(`Ссылка: ${url}`);
});
```

### Использование в промпте:
```javascript
const materialsText = materials.length > 0 
  ? `Материалы пользователя:\n${materials.map((m, i) => `${i+1}. ${m}`).join('\n')}`
  : 'Материалы не предоставлены';

const prompt = `Создай пост для:
${JSON.stringify(payload.answers, null, 2)}

${materialsText}`;
```

## ✅ Преимущества этого формата:

1. **Простота**: Массив строк, как раньше с ссылками
2. **Контекст**: Каждая строка содержит описание + URL
3. **Совместимость**: Легко адаптировать существующий код агента
4. **Читаемость**: Агент видит полную информацию о материале

## 🔄 Миграция из старого формата:

**Было:** `"links": ["url1", "url2"]`  
**Стало:** `"materials": ["описание1 url1", "описание2 url2"]`

Агент может легко извлечь URL как последний элемент после split(' ').
