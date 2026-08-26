# Portainer 生产部署

仓库：<https://github.com/johnhan0313-git/john-readhub>

Cloudflare Tunnel 已配置 `*.cool-app.me` 泛域名转发到 nginx:1180，**无需再改 Tunnel**。

## 前置条件（服务器侧）

- PostgreSQL 库 `readhub` / 用户 `readhub` 已创建
- nginx 已配置 `news.cool-app.me` 路由（见 `deploy/nginx-readhub.conf`）
- **Portainer 挂载 secrets 目录**（一次性，见下）+ `setup-server-secrets.sh`

## Portainer 一次性：挂载共享 token（全项目只需一次）

Portainer **UI 环境变量进不了 `build.args`**；宿主机 `/home/john-han/.secrets` 在 Portainer 容器内默认也**不可见**。做法：把宿主机目录挂进 Portainer，compose 读容器内 `/run/john-secrets/gh_packages_token`。

**1. 写入 token（服务器一次）**

```bash
GH_PACKAGES_TOKEN=ghp_你的token ./scripts/setup-server-secrets.sh
```

**2. 给 Portainer 容器加 volume**（编辑 `~/portainer/portainer-compose.yaml`，参考 `deploy/portainer-compose.example.yaml`）

```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
  - portainer_data:/data
  - /home/john-han/.secrets:/run/john-secrets:ro   # 加这一行
```

```bash
cd ~/portainer && docker compose up -d
```

之后所有 john-* Git Stack **不必**再配 `GH_PACKAGES_TOKEN` 环境变量。

## Portainer Git Stack 部署

1. Portainer → **Stacks** → **Git repository**
2. Repository URL：`https://github.com/johnhan0313-git/john-readhub.git`
3. Compose path：`docker-compose.prod.yml`
4. **Enable relative path volumes**（如 `/home/john-han/apps/john-readhub`）
5. Stack name：**`john-readhub`**
6. **Deploy the stack**（无需 Stack Environment variables 里的 token）

`docker-compose.prod.yml` 已将 backend / frontend 加入外部网络 `john-nginx_default`，**无需**再手动执行 `docker network connect`。

### 代理说明（john-server 必看）

john-server 访问 GitHub / 外网不稳定，分两层：

| 场景 | 配置位置 | 说明 |
|------|----------|------|
| **Portainer 从 GitHub 拉代码** | Portainer 容器自身 | 见下方「Portainer 走 mihomo」 |
| **镜像构建**（pip / npm / next/font） | `docker-compose.prod.yml` → `build.args` | 构建代理默认 `172.17.0.1:7890`；npm 默认 `registry.npmmirror.com` |
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

若 **frontend `npm install` 报 ECONNRESET**（连 registry.npmjs.org 失败），需确保 Git 仓库已包含 `NPM_REGISTRY=registry.npmmirror.com` 的 Dockerfile 改动后再 Pull and redeploy。

若 **frontend 构建报 `GH_PACKAGES_TOKEN is required`**：检查 `setup-server-secrets.sh` 是否已执行，且 Portainer 是否已挂载 `/home/john-han/.secrets:/run/john-secrets:ro` 并重启。

若报 **`failed to stat /home/john-han/.secrets/...`** 或 **`/run/john-secrets/...`**：未挂载或 token 文件不存在；按上文「Portainer 一次性」配置。

若 **frontend 构建在 `npm ci` 失败（401 Unauthorized）**，说明 token 已传入但无效或权限不足，重新生成 PAT 并更新 `GH_PACKAGES_TOKEN`。

若 **compose pull 报 `john-readhub-backend:latest` / `john-readhub-frontend:latest` 400 Bad Request**（经 `mirror.swr.myhuaweicloud.com`），说明 Portainer 在拉取阶段把本地构建镜像当成 Docker Hub 官方镜像去拉了。`docker-compose.prod.yml` 已为 backend / frontend 设置 `pull_policy: build`；Pull 最新代码后 Redeploy。临时绕过可用 SSH 脚本 `./scripts/deploy-john-server.sh`。

若报 **容器名 Conflict**（`john-readhub-backend-1` already in use），说明有手动部署的容器占用了名称。先 `docker rm -f john-readhub-backend-1 john-readhub-frontend-1`，再 Redeploy；或改用 `./scripts/deploy-john-server.sh` 统一管理。

### SSH 部署（推荐）

```bash
chmod +x scripts/deploy-john-server.sh
./scripts/deploy-john-server.sh
```

## 环境变量说明

### 不必配置（compose 内已写死）

| 变量 | 值 |
|------|-----|
| `DATABASE_URL` | `postgresql+psycopg://readhub:readhub-123@john-postgresql:5432/readhub` |
| `USE_MIGRATIONS` | `true` |
| `CORS_ORIGINS` | `https://news.cool-app.me,http://news.cool-app.me` |
| `NEXT_PUBLIC_API_URL`（frontend build） | `/api/v1` |
| `HTTP_PROXY` / `HTTPS_PROXY` | `http://host.docker.internal:7890` | 运行时外网采集走宿主机 mihomo |
| `NO_PROXY` | 内网 + `john-postgresql` | 数据库等内网不走代理 |

### 建议按需配置（写在根目录 `.env` / `.env.test`）

| 变量 | 必填 | 说明 |
|------|------|------|
| `GH_PACKAGES_TOKEN` | **是（构建 frontend）** | 服务器 `setup-server-secrets.sh` + Portainer 挂载 secrets（见上文）；**勿**用 Stack UI 环境变量 |
| `NEWSAPI_KEY` | 否 | [NewsAPI](https://newsapi.org/) 密钥；不配则 NewsAPI 来源采集失败，RSS 仍可用 |
| `GNEWS_API_KEY` | 否 | [GNews](https://gnews.io/) 密钥；不配则 GNews 来源采集失败 |
| `SCRAPER_BOSS_COOKIE` | 否 | BOSS 直聘 Cookie（curl `-b` 整段）；不配则 BOSS 爬虫可能失败 |
| `SCRAPER_MAIMAI_COOKIE` | 否 | 脉脉招聘 Cookie；不配则脉脉爬虫可能失败 |
| `ADMIN_TOKEN` | 是（管理采集） | `X-Admin-Token`；未配置则 admin 返回 503 |

### 一般不用改（有默认值）

| 变量 | 默认 | 说明 |
|------|------|------|
| `FETCH_INTERVAL_MINUTES` | `30` | 非爬虫全量采集间隔（分钟） |
| `RSS_FETCH_INTERVAL_MINUTES` | `15` | RSS 采集间隔 |
| `SCRAPER_FETCH_INTERVAL_MINUTES` | `120` | 招聘爬虫间隔 |
| `ARTICLE_RETENTION_DAYS` | `90` | 文章保留天数 |
| `RUN_FETCH_ON_STARTUP` | `true` | 启动时是否立即采集 |

### Portainer 填表示例

最小部署：`setup-server-secrets.sh` + Portainer 加 volume 并重启，再 redeploy stack。

若要 NewsAPI + 代理爬虫：

```
NEWSAPI_KEY=你的newsapi密钥
SCRAPER_BOSS_COOKIE=lastCity=...; wt2=...; bst=...
```

## 访问

- 站点：https://news.cool-app.me
- API 文档：https://news.cool-app.me/api/docs
- 手动采集：`curl -X POST https://news.cool-app.me/api/v1/admin/fetch -H "X-Admin-Token: $ADMIN_TOKEN"`

## 时间字段说明

API 中所有时间字段均为 **毫秒级 Unix 时间戳**（`long`），例如 `published_at: 1719234567890`。

## 更新 Stack

Portainer → Stacks → john-readhub → **Pull and redeploy**

若 GitHub 拉取超时，先确认 **Portainer 容器** 和 **mihomo** 代理已配置（见上文），再 Pull and redeploy。

## 本地开发

使用 PostgreSQL（与生产相同），先确保 `readhub` 库已创建（见 `scripts/init-postgres.sql`），再：

```bash
cd backend && cp .env.example .env
uvicorn app.main:app --reload --port 8001
```
