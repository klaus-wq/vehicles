FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Системные зависимости для GeoDjango (GEOS, GDAL, PROJ)
# ⚠️ postgis НЕ нужен здесь — это расширение для БД, а не для Python-контейнера
RUN apt-get update && apt-get install -y --no-install-recommends \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    postgresql-client \
    gcc \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && rm -rf /tmp/* /var/tmp/*

# Переменные среды для GDAL (чтобы Python нашёл библиотеки)
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal \
    C_INCLUDE_PATH=/usr/include/gdal

# Установка Python-зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache/pip

# Копирование проекта
COPY . .

# Копируем .env.docker как .env (fallback)
COPY .env.docker .env

# Создаём .env, если файла нет (чтобы не падало при запуске)
RUN if [ ! -f .env ]; then touch .env; fi

# Права на скрипты
RUN mkdir -p scripts && chmod +x scripts/*.sh 2>/dev/null || true

# Непривилегированный пользователь (безопасность)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

# ENTRYPOINT: ждёт БД только если DB_HOST != localhost
ENTRYPOINT ["bash", "-c", "\
    echo '⏳ Проверка БД...' && \
    if [ \"${DB_HOST:-localhost}\" != 'localhost' ]; then \
        until pg_isready -h ${DB_HOST:-db} -U ${POSTGRES_USER:-vehicleuser2} -d ${POSTGRES_DB:-vehicles5} &>/dev/null; do sleep 1; done; \
    fi && \
    python manage.py migrate --noinput && \
    python manage.py shell -c \"from django.contrib.auth import get_user_model; User=get_user_model(); User.objects.create_superuser('admin','admin@example.com','admin123')\" 2>/dev/null || true && \
    exec python manage.py runserver 0.0.0.0:8080"]