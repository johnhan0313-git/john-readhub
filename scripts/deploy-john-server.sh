#!/usr/bin/env bash
# 通过 rsync + docker compose 部署到 john-server，绕过 Portainer 从 GitHub 构建失败。
# 用法：./scripts/deploy-john-server.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REMOTE="${JOHN_SERVER:-john-server}"
REMOTE_DIR="${REMOTE_DIR:-/home/john-han/apps/john-readhub}"
ENV_FILE="${ENV_FILE:-.env.prod}"

echo "→ rsync to ${REMOTE}:${REMOTE_DIR}"
ssh "${REMOTE}" "mkdir -p '${REMOTE_DIR}'"
rsync -avz --delete \
  --exclude .git \
  --exclude node_modules \
  --exclude frontend/node_modules \
  --exclude frontend/.next \
  --exclude backend/.venv \
  --exclude backend/__pycache__ \
  --exclude backend/.env \
  --exclude backend/data \
  --exclude .env.prod \
  --exclude '**/__pycache__' \
  --exclude '.cursor' \
  --exclude '.run' \
  "${ROOT}/" "${REMOTE}:${REMOTE_DIR}/"

echo "→ docker build & up"
ssh "${REMOTE}" bash -s <<EOF
set -euo pipefail
cd "${REMOTE_DIR}"
if [[ ! -f "${ENV_FILE}" ]]; then
  cp .env.prod.example "${ENV_FILE}"
  echo "已创建 ${ENV_FILE}（默认值），可按需编辑 API Key 等"
fi
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
chmod +x scripts/docker-build.sh
BUILD_MEMORY="\${BUILD_MEMORY:-4g}" ./scripts/docker-build.sh
# 清理占用固定 container_name 的旧容器（避免 Portainer / 手动部署冲突）
docker rm -f john-readhub-backend-1 john-readhub-frontend-1 2>/dev/null || true
docker compose --env-file "${ENV_FILE}" -f docker-compose.prod.yml up -d --no-build --remove-orphans
docker compose -f docker-compose.prod.yml ps
EOF

echo "✓ 部署完成"
echo "  https://news.cool-app.me"
