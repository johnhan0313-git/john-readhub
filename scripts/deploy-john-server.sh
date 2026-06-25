#!/usr/bin/env bash
# 通过 rsync + docker compose 部署到 john-server，绕过 Portainer 从 GitHub 构建失败。
# 用法：
#   ./scripts/deploy-john-server.sh
#   DEPLOY_ENV=test ./scripts/deploy-john-server.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REMOTE="${JOHN_SERVER:-john-server}"
REMOTE_DIR="${REMOTE_DIR:-/home/john-han/apps/john-readhub}"
DEPLOY_ENV="${DEPLOY_ENV:-prod}"
if [[ "${DEPLOY_ENV}" == "test" ]]; then
  ENV_FILE=".env.test"
else
  ENV_FILE=".env"
fi

echo "→ rsync to ${REMOTE}:${REMOTE_DIR} (env: ${DEPLOY_ENV})"
ssh "${REMOTE}" "mkdir -p '${REMOTE_DIR}'"
rsync -avz --delete \
  --exclude .git \
  --exclude node_modules \
  --exclude frontend/node_modules \
  --exclude frontend/.next \
  --exclude backend/.venv \
  --exclude backend/__pycache__ \
  --exclude backend/.env \
  --exclude '**/__pycache__' \
  --exclude '.cursor' \
  --exclude '.run' \
  "${ROOT}/" "${REMOTE}:${REMOTE_DIR}/"

echo "→ docker build & up"
ssh "${REMOTE}" bash -s <<EOF
set -euo pipefail
cd "${REMOTE_DIR}"
SHARED="${GH_PACKAGES_TOKEN_FILE:-/home/john-han/.secrets/gh_packages_token}"
if [[ ! -f "\${SHARED}" ]]; then
  echo "错误: 未找到 \${SHARED}，请在 john-server 执行一次 scripts/setup-server-secrets.sh" >&2
  exit 1
fi
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
chmod +x scripts/docker-build.sh
ENV_FILE="${ENV_FILE}" BUILD_MEMORY="\${BUILD_MEMORY:-4g}" ./scripts/docker-build.sh
docker rm -f john-readhub-backend-1 john-readhub-frontend-1 2>/dev/null || true
COMPOSE_ENV=()
if [[ -f "${ENV_FILE}" ]]; then
  COMPOSE_ENV=(--env-file "${ENV_FILE}")
fi
docker compose "\${COMPOSE_ENV[@]}" -f docker-compose.prod.yml up -d --no-build --remove-orphans
docker compose -f docker-compose.prod.yml ps
EOF

echo "✓ 部署完成 (${DEPLOY_ENV})"
echo "  https://news.cool-app.me"
