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

### 代理说明（john-server 必看）

john-server 访问 GitHub / 外网不稳定，分两层：

| 场景 | 配置位置 | 说明 |
|------|----------|------|
| **Portainer 从 GitHub 拉代码** | Portainer 容器自身 | 见下方「Portainer 走 mihomo」 |
| **镜像构建**（pip / npm / next/font） | `docker-compose.prod.yml` → `build.args` | 已默认走 `172.17.0.1:7890`（docker0 网关；Portainer BuildKit 不保证 `build.extra_hosts` 生效） |
| **运行时采集**（RSS / API / LLM） | backend `environment` | 已默认走 mihomo；httpx 自动读 `HTTP_PROXY` |

#### 让 Portainer 走 mihomo 代理（拉 GitHub 用）

与 john-english-study 相同，在 **Portainer 容器**（非本 Stack）配置：

```yaml
# ~/portainer/portainer-compose.yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
environment:
  HTTP_PROXY: http://host.docker.internal:7890
  HTTPS_PROXY: http://host.docker.internal:7890
  NO_PROXY: localhost,127.0.0.1,192.168.0.0/16,10.0.0.0/8,172.16.0.0/12
```

修改后 `docker compose up -d` 重启 Portainer。**mihomo 必须保持运行**（监听 `7890`），否则 Pull 仍会超时。

Pull 失败但容器仍在跑时，**不要反复点 Pull**；确认 mihomo 正常后重试一次即可。

若 Stack 长时间卡在 **frontend `next build`**（日志出现 `socket hang up` / `Retrying 1/3`），多为构建容器无法解析 `host.docker.internal`、Google Fonts 下载失败。当前 `docker-compose.prod.yml` 构建代理已改为 `172.17.0.1:7890`；旧 Stack 需 Pull and redeploy 后才会生效。

## 环境变量说明

### 不必配置（compose 内已写死）

| 变量 | 值 |
|------|-----|
| `DATABASE_URL` | `postgresql+psycopg://readhub:readhub-123@john-postgresql:5432/readhub` |
| `USE_MIGRATIONS` | `true` |
| `CORS_ORIGINS` | `https://news.cool-app.me,http://news.cool-app.me` |
| `NEXT_PUBLIC_API_URL`（frontend build） | `/api` |
| `HTTP_PROXY` / `HTTPS_PROXY` | `http://host.docker.internal:7890` | 运行时外网采集走宿主机 mihomo |
| `NO_PROXY` | 内网 + `john-postgresql` | 数据库等内网不走代理 |

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

若 GitHub 拉取超时，先确认 **Portainer 容器** 和 **mihomo** 代理已配置（见上文），再 Pull and redeploy。

## 本地开发

仍默认 SQLite，无需 PostgreSQL：

```bash
cd backend && cp .env.example .env
uvicorn app.main:app --reload --port 8001
```
