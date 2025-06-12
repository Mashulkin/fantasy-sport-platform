# Fantasy Sports Platform

Платформа для управления фэнтези-спорт турнирами с автоматизированным сбором данных.

## Быстрый старт

### Требования
- Docker и Docker Compose
- Git

### Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone <your-repo>
cd fantasy-sports-platform
```

2. Создайте `.env` файл из примера:
```bash
cp .env.example .env
```

3. Отредактируйте `.env` файл, особенно:
- `SECRET_KEY` - поменяйте на случайную строку
- `FIRST_SUPERUSER` и `FIRST_SUPERUSER_PASSWORD` - данные админа

4. Запустите проект:
```bash
docker-compose up -d
```

5. Проверьте, что все контейнеры запустились:
```bash
docker-compose ps
```

### Доступ к сервисам

- **Frontend**: http://localhost (через Nginx)
- **Backend API**: http://localhost/api/v1
- **API Документация**: http://localhost/docs
- **Альтернативная документация**: http://localhost/redoc
- **База данных**: localhost:5432
- **Redis**: localhost:6379

### Первый вход

1. Откройте http://localhost
2. Перейдите на страницу входа
3. Используйте данные из `.env`:
   - Email: значение `FIRST_SUPERUSER`
   - Пароль: значение `FIRST_SUPERUSER_PASSWORD`

## Разработка

### Backend (FastAPI)

Для разработки backend:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend (Vue.js)

Для разработки frontend:

```bash
cd frontend
npm install
npm run dev
```

### Создание миграций БД

```bash
docker-compose exec backend alembic revision --autogenerate -m "Description"
docker-compose exec backend alembic upgrade head
```

## Структура проекта

```
fantasy-sports-platform/
├── backend/         # FastAPI приложение
├── frontend/        # Vue.js приложение  
├── nginx/          # Nginx конфигурация
└── docker-compose.yml
```

## Полезные команды

### Логи
```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f backend
```

### Перезапуск
```bash
docker-compose restart backend
```

### Остановка
```bash
docker-compose down
```

### Полная очистка (включая volumes)
```bash
docker-compose down -v
```

## Следующие шаги

1. Настройте Alembic для миграций
2. Добавьте модели для игроков, команд и турниров
3. Создайте парсеры для импорта данных
4. Настройте Celery для фоновых задач
5. Разработайте интерфейс для просмотра данных

## Troubleshooting

### Ошибка подключения к БД
Убедитесь, что контейнер `db` запущен и готов:
```bash
docker-compose logs db
```

### Frontend не обновляется
Очистите кэш браузера или перезапустите контейнер:
```bash
docker-compose restart frontend
```
# Настройка Celery для Fantasy Sports Platform

## Обзор

Celery используется для запуска парсеров по расписанию и выполнения фоновых задач.

## Компоненты

1. **Celery Worker** - выполняет задачи
2. **Celery Beat** - планировщик задач
3. **Flower** - веб-интерфейс для мониторинга
4. **Redis** - брокер сообщений

## Запуск

### 1. Запуск всех сервисов

```bash
docker-compose up -d
```

Это запустит:
- Backend API
- Celery Worker
- Celery Beat
- Flower (веб-интерфейс)
- Redis
- PostgreSQL

### 2. Проверка статуса

```bash
# Проверить все контейнеры
docker-compose ps

# Логи Celery Worker
docker-compose logs -f celery_worker

# Логи Celery Beat
docker-compose logs -f celery_beat
```

### 3. Доступ к интерфейсам

- **Flower** (мониторинг Celery): http://localhost:5555
- **API документация**: http://localhost/docs
- **Основное приложение**: http://localhost

## Управление парсерами

### Через веб-интерфейс

1. Войдите в систему как администратор
2. Перейдите в раздел Admin → Parser Management
3. Здесь можно:
   - Создавать новые парсеры
   - Настраивать расписание (cron формат)
   - Запускать парсеры вручную
   - Просматривать логи выполнения

### Через API

```bash
# Получить список парсеров
curl -X GET http://localhost/api/v1/parsers \
  -H "Authorization: Bearer YOUR_TOKEN"

# Запустить парсер вручную
curl -X POST http://localhost/api/v1/parsers/1/run \
  -H "Authorization: Bearer YOUR_TOKEN"

# Проверить статус задачи
curl -X GET http://localhost/api/v1/parsers/task/TASK_ID/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Формат расписания (Cron)

Парсеры используют cron-формат для расписания:

```
* * * * *
│ │ │ │ │
│ │ │ │ └─── день недели (0 - 7) (0 или 7 = воскресенье)
│ │ │ └───── месяц (1 - 12)
│ │ └─────── день месяца (1 - 31)
│ └───────── час (0 - 23)
└─────────── минута (0 - 59)
```

Примеры:
- `0 */4 * * *` - каждые 4 часа
- `0 */2 * * *` - каждые 2 часа
- `0 0 * * *` - каждый день в полночь
- `*/15 * * * *` - каждые 15 минут
- `0 9,21 * * *` - в 9:00 и 21:00

## Создание нового парсера

### 1. Создать класс парсера

Создайте файл `backend/app/parsers/your_platform/your_parser.py`:

```python
from app.parsers.base import BaseParser

class YourParser(BaseParser):
    async def parse(self):
        # Логика получения данных
        data = await fetch_data()
        return data
    
    async def save_to_db(self, data):
        # Логика сохранения в БД
        pass
```

### 2. Зарегистрировать парсер

В файле `backend/app/services/parser_service.py`:

```python
from app.parsers.your_platform.your_parser import YourParser

PARSER_REGISTRY = {
    "fpl_players": FPLPlayersParser,
    "fpl_ownership": FPLOwnershipParser,
    "your_parser": YourParser,  # Добавить здесь
}
```

### 3. Создать конфигурацию в БД

Через веб-интерфейс или API создайте конфигурацию парсера:
- Name: "Your Parser Name"
- Platform: "YOUR_PLATFORM"
- Parser Type: "your_parser"
- Schedule: "0 */6 * * *"
- Active: true

## Мониторинг

### Flower

Откройте http://localhost:5555 для доступа к Flower:
- **Tasks** - список выполненных задач
- **Workers** - активные воркеры
- **Broker** - очередь задач
- **Monitor** - графики производительности

### Логи парсеров

Логи сохраняются в БД и доступны через:
1. Веб-интерфейс: Admin → Parser Management → Logs
2. API: GET `/api/v1/parsers/{parser_id}/logs`

### Health Check

Система автоматически проверяет состояние парсеров каждый час.
Если парсер не запускался более 24 часов, создается алерт.

## Отладка

### Проблемы с запуском

```bash
# Проверить логи конкретного сервиса
docker-compose logs -f celery_worker
docker-compose logs -f celery_beat

# Перезапустить сервисы
docker-compose restart celery_worker celery_beat

# Полная переустановка
docker-compose down
docker-compose up -d
```

### Проблемы с расписанием

1. Проверьте, что парсер активен (is_active = true)
2. Проверьте корректность cron выражения
3. Убедитесь, что Celery Beat запущен
4. Проверьте логи: `docker-compose logs celery_beat`

### Ручное обновление расписаний

```bash
# Войти в контейнер backend
docker-compose exec backend bash

# Запустить скрипт обновления
python scripts/init_celery_schedules.py
```

## Производительность

### Настройки воркера

В `docker-compose.yml` для celery_worker:
- `--concurrency=4` - количество процессов (по умолчанию = CPU cores)
- `--max-tasks-per-child=100` - перезапуск после N задач
- `--pool=prefork` - тип пула (prefork для CPU-bound задач)

### Оптимизация

1. Для Windows используется `--pool=solo` (один процесс)
2. Для Linux можно использовать `--pool=prefork --concurrency=4`
3. Настройте лимиты времени в `celery_app.py`:
   - `task_time_limit` - жесткий лимит
   - `task_soft_time_limit` - мягкий лимит

## Безопасность

1. Измените `SECRET_KEY` в `.env`
2. Используйте сильные пароли для Redis
3. Ограничьте доступ к Flower (добавьте аутентификацию)
4. Регулярно проверяйте логи на ошибки