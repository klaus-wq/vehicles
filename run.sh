#!/bin/bash
# test.sh — запуск Vehicles Demo одной командой
set -e

echo "🚀 Запуск Vehicles Demo..."

# 1. Проверка Docker
if ! command -v docker &>/dev/null || ! docker info &>/dev/null; then
    echo "❌ Docker не установлен или не запущен."
    echo "👉 Скачайте: https://docs.docker.com/get-docker/"
    exit 1
fi

# 2. Запуск контейнеров
echo "🐳 Запуск базы данных и веб-приложения..."
docker compose up -d

# 3. Ожидание готовности PostgreSQL
echo "⏳ Ожидание базы данных..."
for i in {1..30}; do
    if docker compose exec db pg_isready -U vehicleuser2 -d vehicles5 &>/dev/null; then
        echo "✅ База данных готова"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Таймаут ожидания БД. Проверьте логи: docker compose logs db"
        exit 1
    fi
    sleep 2
done

# 4. Ожидание готовности веб-сервера
echo "⏳ Ожидание веб-сервера..."
for i in {1..30}; do
    if curl -s http://localhost:8080/admin &>/dev/null; then
        echo "✅ Веб-сервер запущен"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Таймаут ожидания веба. Проверьте логи: docker compose logs web"
        exit 1
    fi
    sleep 2
done

# 5. Итог
echo ""
echo "🎉 Готово! Проект запущен:"
echo "🌐 Приложение: http://localhost:8080"
echo "🔐 Админка:     http://localhost:8080/admin"
echo "   Логин: admin / Пароль: admin123"
echo "📡 API:       http://localhost:8080/api/vehicles/"
echo ""
echo "🛠 Управление:"
echo "   • Остановить:      docker compose down"
echo "   • Удалить данные:  docker compose down -v"
echo "   • Смотреть логи:   docker compose logs -f"