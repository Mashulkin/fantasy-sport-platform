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
