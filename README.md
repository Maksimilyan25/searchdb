# Document Search Service

Сервис для полнотекстового поиска по документам с использованием PostgreSQL и Elasticsearch.

## 🚀 Быстрый старт

# Запуск всех сервисов
docker-compose up -d --build


При первом запуске автоматически:

Применяются миграции Alembic

Загружаются тестовые данные из data/posts.csv (если БД пустая)

Создается индекс в Elasticsearch

Команды
# Запуск
docker-compose up -d

# Пересборка
docker-compose up -d --build

# Остановка
docker-compose down

# Логи
docker logs -f search_app

# Проверка health
curl http://localhost:8000/health

📚 API
Документация: http://localhost:8000/docs



Поиск документов
curl "http://localhost:8000/api/v1/search?q=макияж"

Удаление документа
curl -X DELETE "http://localhost:8000/api/v1/documents/1"


 Структура проекта
text
├── src/
│   ├── api/          # Роуты и схемы
│   ├── core/         # Конфиг, БД, логгер
│   ├── models/       # SQLAlchemy модели
│   ├── repositories/ # Репозитории
│   └── services/     # Бизнес-логика
├── data/             # Тестовые данные
├── migrations/       # Alembic миграции
├── docker-compose.yml
└── Dockerfile


🛠️ Технологии
FastAPI
PostgreSQL 15
Elasticsearch 8
SQLAlchemy 2.0
Alembic
Docker

