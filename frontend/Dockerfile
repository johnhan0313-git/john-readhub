# syntax=docker/dockerfile:1

FROM node:20-alpine AS base

ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY
ARG NPM_REGISTRY=https://registry.npmmirror.com

FROM base AS deps
ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY
ARG NPM_REGISTRY
ARG GH_PACKAGES_TOKEN
ARG GITHUB_TOKEN
ENV HTTP_PROXY=$HTTP_PROXY HTTPS_PROXY=$HTTPS_PROXY NO_PROXY=$NO_PROXY
WORKDIR /app
COPY package.json package-lock.json* ./
RUN --mount=type=secret,id=gh_packages_token,required=false \
    TOKEN="$(cat /run/secrets/gh_packages_token 2>/dev/null || true)" \
    && TOKEN="${TOKEN:-${GH_PACKAGES_TOKEN:-${GITHUB_TOKEN}}}" \
    && test -n "$TOKEN" || (echo "GH_PACKAGES_TOKEN required: 服务器运行 scripts/setup-server-secrets.sh，或本地 export / .env" >&2 && exit 1) \
    && printf '@johnhan0313-git:registry=https://npm.pkg.github.com\n//npm.pkg.github.com/:_authToken=%s\nalways-auth=true\n' "$TOKEN" > .npmrc \
    && npm config set registry "${NPM_REGISTRY}" \
    && if [ -f package-lock.json ]; then npm ci; else npm install; fi

FROM base AS builder
ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY
ARG NEXT_PUBLIC_API_URL=http://localhost:8001/api
ENV HTTP_PROXY=$HTTP_PROXY HTTPS_PROXY=$HTTPS_PROXY NO_PROXY=$NO_PROXY
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY package.json package-lock.json* ./
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
USER nextjs
EXPOSE 3001
ENV PORT=3001
ENV HOSTNAME="0.0.0.0"
CMD ["node", "server.js"]
