#!/usr/bin/env bash
set -euo pipefail

: "${REMOTE_USER:=root}"
: "${REMOTE_HOST:=72.56.34.61}"
: "${REMOTE_PORT:=22}"
: "${DEPLOY_DIR:=/opt/vehicles}"
: "${DOCKER_FILE:=docker-compose.yml}"
: "${DJANGO_SECRET_KEY:=change-me}"
: "${POSTGRES_PASSWORD:=admin}"

SSH="ssh -o StrictHostKeyChecking=accept-new -p ${REMOTE_PORT} ${REMOTE_USER}@${REMOTE_HOST}"

log() { echo "[$(date '+%H:%M:%S')] $*"; }

# 1. Проверка SSH
log "Подключение..."
$SSH "echo OK" || { log "SSH недоступен"; exit 1; }

# 2. Установка Docker (если нет)
log "Docker..."
$SSH '
  export PATH="/usr/bin:/usr/local/bin:$PATH"
  command -v docker || pacman -Sy --noconfirm archlinux-keyring docker docker-compose rsync
  systemctl enable --now docker 2>/dev/null || true
'

# 3. Бэкап
log "Бэкап..."
BACKUP="${DEPLOY_DIR}_backup_$(date +%Y%m%d)"
$SSH "test -d ${DEPLOY_DIR} && cp -a ${DEPLOY_DIR} ${BACKUP} || mkdir -p ${DEPLOY_DIR}"

# 4. Синхронизация кода
log "Код..."
rsync -avz --delete -e "ssh -p ${REMOTE_PORT}" \
  --exclude='.git' --exclude='.venv' --exclude='*.pyc' --exclude='postgres_data' \
  ./ "${REMOTE_USER}@${REMOTE_HOST}:${DEPLOY_DIR}/"

# 5. Генерация .env
log ".env..."
$SSH "cat > ${DEPLOY_DIR}/.env << EOF
DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
DJANGO_DEBUG=0
ALLOWED_HOSTS=*
POSTGRES_DB=vehicles5
POSTGRES_USER=vehicleuser2
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
DATABASE_URL=postgres://vehicleuser2:${POSTGRES_PASSWORD}@db:5432/vehicles5
EOF
chmod 600 ${DEPLOY_DIR}/.env"

# 6. Запуск
log "Запуск..."
$SSH "cd ${DEPLOY_DIR} && docker compose -f ${DOCKER_FILE} up -d --build"

# 7. Health-check
log "Проверка..."
for i in {1..10}; do
  $SSH "curl -sf http://127.0.0.1:8080/admin/login/ &>/dev/null" && { log "✅ Готово!"; break; }
  log "⏳ Попытка $i/10..."
  sleep 5
done

log "Деплой завершён: http://${REMOTE_HOST}:8080"