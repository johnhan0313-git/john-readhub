#!/usr/bin/env bash
# 带内存上限的镜像构建（Compose v5 尚不支持 build.memory）
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"

SHARED_TOKEN_FILE="${GH_PACKAGES_TOKEN_FILE:-/home/john-han/.secrets/gh_packages_token}"

DEPLOY_ENV="${DEPLOY_ENV:-prod}"
if [[ "${DEPLOY_ENV}" == "test" ]]; then
  ENV_FILE="${ENV_FILE:-.env.test}"
else
  ENV_FILE="${ENV_FILE:-.env}"
fi
if [[ -z "${GH_PACKAGES_TOKEN:-}" && -z "${GITHUB_TOKEN:-}" && -f "${ENV_FILE}" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
  set +a
fi

GH_PACKAGES_TOKEN="${GH_PACKAGES_TOKEN:-${GITHUB_TOKEN:-}}"
if [[ -z "${GH_PACKAGES_TOKEN}" && -f "${SHARED_TOKEN_FILE}" ]]; then
  GH_PACKAGES_TOKEN="$(tr -d '[:space:]' < "${SHARED_TOKEN_FILE}")"
fi

BUILD_MEMORY="${BUILD_MEMORY:-4g}"
BUILD_HTTP_PROXY="${BUILD_HTTP_PROXY:-http://172.17.0.1:7890}"
BUILD_HTTPS_PROXY="${BUILD_HTTPS_PROXY:-http://172.17.0.1:7890}"
NO_PROXY="${NO_PROXY:-localhost,127.0.0.1,john-postgresql,192.168.0.0/16,10.0.0.0/8,172.16.0.0/12}"
NPM_REGISTRY="${NPM_REGISTRY:-https://registry.npmmirror.com}"
NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-/api}"

if [[ -z "${GH_PACKAGES_TOKEN}" && ! -f "${SHARED_TOKEN_FILE}" ]]; then
  echo "错误: 未找到 GitHub Packages token。服务器执行 scripts/setup-server-secrets.sh，或本地 .env / export GH_PACKAGES_TOKEN" >&2
  exit 1
fi

BACKEND_IMAGE="${BACKEND_IMAGE:-john-readhub-backend:latest}"
FRONTEND_IMAGE="${FRONTEND_IMAGE:-john-readhub-frontend:latest}"

echo "→ build backend (--memory=${BUILD_MEMORY})"
docker build --memory="${BUILD_MEMORY}" \
  --build-arg "HTTP_PROXY=${BUILD_HTTP_PROXY}" \
  --build-arg "HTTPS_PROXY=${BUILD_HTTPS_PROXY}" \
  --build-arg "NO_PROXY=${NO_PROXY}" \
  -t "${BACKEND_IMAGE}" \
  -f backend/Dockerfile backend/

echo "→ build frontend (--memory=${BUILD_MEMORY})"
FRONTEND_BUILD=(
  docker build --memory="${BUILD_MEMORY}"
  --build-arg "HTTP_PROXY=${BUILD_HTTP_PROXY}"
  --build-arg "HTTPS_PROXY=${BUILD_HTTPS_PROXY}"
  --build-arg "NO_PROXY=${NO_PROXY}"
  --build-arg "NPM_REGISTRY=${NPM_REGISTRY}"
  --build-arg "NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}"
)
if [[ -n "${GH_PACKAGES_TOKEN}" ]]; then
  FRONTEND_BUILD+=(--build-arg "GH_PACKAGES_TOKEN=${GH_PACKAGES_TOKEN}")
fi
FRONTEND_BUILD+=(-t "${FRONTEND_IMAGE}" -f frontend/Dockerfile frontend/)
"${FRONTEND_BUILD[@]}"
