# Portainer 生产部署

仓库：<https://github.com/johnhan0313-git/john-readhub>

Cloudflare Tunnel 已配置 `*.cool-app.me` 泛域名转发到 nginx:1180，**无需再改 Tunnel**。

## 前置条件（服务器侧，已完成）

- PostgreSQL 库 `readhub` / 用户 `readhub` 已创建
- nginx 已配置 `news.cool-app.me` 路由（见 `deploy/nginx-readhub.conf`）

## Portainer Git Stack 部署

1. Portainer → **Stacks** → **Add stack** → **Git repository**
2. Repository URL：`https://github.com/johnhan0313-git/john-readhub.git`
3. Compose path：`docker-compose.prod.yml`
4. **Stack name 填 `john-readhub`**（与 nginx 中容器名一致）
5. 在 **Environment variables** 中按需填入（见下表）
6. **Deploy the stack**

`docker-compose.prod.yml` 已将 backend / frontend 加入外部网络 `john-nginx_default`，**无需**再手动执行 `docker network connect`。

## 环境变量说明

### 不必配置（compose 内已写死）

| 变量 | 值 |
|------|-----|
| `DATABASE_URL` | `postgresql+psycopg://readhub:readhub-123@john-postgresql:5432/readhub` |
| `USE_MIGRATIONS` | `true` |
| `CORS_ORIGINS` | `https://news.cool-app.me,http://news.cool-app.me` |
| `NEXT_PUBLIC_API_URL`（frontend build） | `/api` |
| `HTTP_PROXY` / `HTTPS_PROXY` | `http://host.docker.internal:7890`（走宿主机 mihomo） |
| `NO_PROXY` | 内网地址 + `john-postgresql` |

### 建议按需配置（Portainer Environment variables）

| 变量 | 必填 | 说明 |
|------|------|------|
| `NEWSAPI_KEY` | 否 | [NewsAPI](https://newsapi.org/) 密钥；不配则 NewsAPI 来源采集失败，RSS 仍可用 |
| `GNEWS_API_KEY` | 否 | [GNews](https://gnews.io/) 密钥；不配则 GNews 来源采集失败 |
| `SCRAPER_BOSS_COOKIE` | 否 | BOSS 直聘 Cookie（curl `-b` 整段）；不配则 BOSS 爬虫可能失败 |
| `SCRAPER_MAIMAI_COOKIE` | 否 | 脉脉招聘 Cookie；不配则脉脉爬虫可能失败 |
| `AI_LLM_API_KEY` | 否 | 事件聚类 LLM 密钥；不配则 `POST /api/admin/cluster-events` 跳过 |

### 一般不用改（有默认值）

| 变量 | 默认 | 说明 |
|------|------|------|
| `FETCH_INTERVAL_MINUTES` | `30` | 全量采集间隔（分钟） |
| `RSS_FETCH_INTERVAL_MINUTES` | `15` | RSS 采集间隔 |
| `SCRAPER_FETCH_INTERVAL_MINUTES` | `120` | 招聘爬虫间隔 |
| `ARTICLE_RETENTION_DAYS` | `90` | 文章保留天数 |
| `RUN_FETCH_ON_STARTUP` | `true` | 启动时是否立即采集 |
| `AI_LLM_BASE_URL` | `https://api.openai.com/v1` | LLM API 地址 |
| `AI_LLM_MODEL` | `gpt-4o-mini` | LLM 模型 |

### Portainer 填表示例

最小部署（仅 RSS，无 API Key）**可以不填任何 Environment variables**，直接 Deploy。

若要 NewsAPI + 代理爬虫：

```
NEWSAPI_KEY=你的newsapi密钥
SCRAPER_BOSS_COOKIE=lastCity=...; wt2=...; bst=...
```

## 访问

- 站点：https://news.cool-app.me
- API 文档：https://news.cool-app.me/api/docs
- 手动采集：`curl -X POST https://news.cool-app.me/api/admin/fetch`

## 时间字段说明

API 中所有时间字段均为 **毫秒级 Unix 时间戳**（`long`），例如 `published_at: 1719234567890`。

## 更新 Stack

Portainer → Stacks → john-readhub → **Pull and redeploy**

若 GitHub 拉取超时，稍等重试或检查服务器 mihomo 是否运行。

## 本地开发

仍默认 SQLite，无需 PostgreSQL：

```bash
cd backend && cp .env.example .env
uvicorn app.main:app --reload --port 8001
```
