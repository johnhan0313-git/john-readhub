#!/usr/bin/env bash
# 带内存上限的镜像构建（Compose v5 尚不支持 build.memory）
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"

ENV_FILE="${ENV_FILE:-.env.prod}"
if [[ -z "${GITHUB_TOKEN:-}" && -f "${ENV_FILE}" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
  set +a
fi

BUILD_MEMORY="${BUILD_MEMORY:-4g}"
BUILD_HTTP_PROXY="${BUILD_HTTP_PROXY:-http://172.17.0.1:7890}"
BUILD_HTTPS_PROXY="${BUILD_HTTPS_PROXY:-http://172.17.0.1:7890}"
NO_PROXY="${NO_PROXY:-localhost,127.0.0.1,john-postgresql,192.168.0.0/16,10.0.0.0/8,172.16.0.0/12}"
NPM_REGISTRY="${NPM_REGISTRY:-https://registry.npmmirror.com}"
NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-/api}"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"

if [[ -z "${GITHUB_TOKEN}" ]]; then
  echo "错误: GITHUB_TOKEN 未设置。frontend 依赖 @johnhan0313-git/shared（GitHub Packages），构建前需 export GITHUB_TOKEN=ghp_..." >&2
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
docker build --memory="${BUILD_MEMORY}" \
  --build-arg "HTTP_PROXY=${BUILD_HTTP_PROXY}" \
  --build-arg "HTTPS_PROXY=${BUILD_HTTPS_PROXY}" \
  --build-arg "NO_PROXY=${NO_PROXY}" \
  --build-arg "NPM_REGISTRY=${NPM_REGISTRY}" \
  --build-arg "GITHUB_TOKEN=${GITHUB_TOKEN}" \
  --build-arg "NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}" \
  -t "${FRONTEND_IMAGE}" \
  -f frontend/Dockerfile frontend/
