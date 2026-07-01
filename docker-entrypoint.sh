#!/bin/sh
set -e

echo "🚀 Запуск приложения..."

# Применяем миграции
echo "🔄 Применяем миграции..."
alembic upgrade head

# Запускаем приложение
echo "✅ Миграции применены, запускаем uvicorn..."
exec uvicorn main:app --host 0.0.0.0 --port 8000