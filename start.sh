#!/bin/bash
# start.sh - синхронизация локальной БД в Docker
set -e

# === НАСТРОЙКИ ===
DB_HOST="127.0.0.1"
DB_PORT="5432"
DB_NAME="vehicles5"
DB_USER="vehicleuser2"
DB_PASS="${DB_PASS:-admin}"
SQL_FILE="/tmp/vehicles5_sync.sql"

echo "🔄 Синхронизация БД: локаль → Docker"

# 1. Создание SQL-дампа
echo "📦 Создание дампа..."
PGPASSWORD="$DB_PASS" pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --format=plain \
    --clean \
    --if-exists \
    --no-owner \
    --no-acl \
    -f "$SQL_FILE"

echo "   ✅ Дамп создан: $(du -h "$SQL_FILE" | cut -f1)"

# 2. Запуск БД в Docker
echo "🐳 Запуск PostgreSQL в Docker..."
docker compose up -d db

# Ожидание готовности
echo "⏳ Ожидание готовности БД..."
for i in {1..30}; do
    if docker compose exec db pg_isready -U "$DB_USER" -d "$DB_NAME" &>/dev/null; then
        echo "   ✅ БД готова"
        break
    fi
    sleep 1
done

# 3. Восстановление данных
echo "🔄 Восстановление данных..."
docker compose cp "$SQL_FILE" db:/tmp/restore.sql
docker compose exec \
  -e PGOPTIONS="-c statement_timeout=0 -c client_min_messages=WARNING" \
  db \
  psql -U "$DB_USER" -d "$DB_NAME" -q -f /tmp/restore.sql

echo "✅ Синхронизация завершена!"

# 4. Запуск веб-интерфейса и проверка
echo "📊 Запуск веб-интерфейса и проверка..."
docker compose up -d web
sleep 5
docker compose exec web python manage.py shell -c "
from vehicle.models import Vehicle
from telemetry.models import TelemetryPoint
print(f'   🚗 Автомобилей: {Vehicle.objects.count()}')
print(f'   📡 Точек телеметрии: {TelemetryPoint.objects.count():,}')
"