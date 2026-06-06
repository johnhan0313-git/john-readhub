# ReadHub — 新闻聚合阅读平台

多源新闻爬取、分类汇总与阅读网站。通过 RSS 与第三方新闻 API 采集最新资讯，支持分类浏览、搜索与按日期时间线展示。

## 功能

- **多源采集**：RSS（36氪、少数派、IT之家、新华网、中国新闻网等国内源 + Hacker News、BBC 等）+ NewsAPI / GNews（可选 API Key，含中国区）
- **分类汇总**：科技、IT技术、财经、商业、国内、国际、体育、娱乐、健康、汽车、教育、育儿、美食、职场、招聘、综合（16 类）
- **去重**：URL 规范化哈希 + 标题模糊匹配
- **文章时间线**：按日期分组展示新闻流
- **定时任务**：启动时自动采集，RSS 每 15 分钟、全量每 30 分钟
- **二期预留**：AI 事件聚类 API（`POST /api/admin/cluster-events`）

## 端口说明

| 服务 | 端口 |
|------|------|
| 前端（Next.js） | **3001** |
| 后端（FastAPI） | **8001** |

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 20+

### 使用 Docker Compose（推荐）

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
docker compose up --build
```

访问 http://localhost:3001 ，API 文档 http://localhost:8001/docs

### 本地开发

**1. 后端**（SQLite，数据文件 `backend/data/readhub.db`）

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8001
```

**2. 前端**

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

访问 http://localhost:3001

### 手动触发采集

```bash
curl -X POST http://localhost:8001/api/admin/fetch
```

## 环境变量

| 变量 | 说明 |
|------|------|
| `DATABASE_URL` | 默认 `sqlite:///./data/readhub.db` |
| `NEWSAPI_KEY` | [NewsAPI](https://newsapi.org/) 密钥（可选） |
| `GNEWS_API_KEY` | [GNews](https://gnews.io/) 密钥（可选） |
| `FETCH_INTERVAL_MINUTES` | 全量采集间隔，默认 30 |
| `RSS_FETCH_INTERVAL_MINUTES` | RSS 采集间隔，默认 15 |
| `AI_LLM_API_KEY` | 事件聚类用 LLM 密钥（二期，可选） |

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/articles` | 文章列表（分页、分类、搜索） |
| GET | `/api/articles/{id}` | 文章详情 |
| GET | `/api/categories` | 分类及文章数 |
| GET | `/api/timeline` | 按日期分组的时间线 |
| GET | `/api/sources` | 数据源列表 |
| POST | `/api/admin/fetch` | 手动触发采集 |
| POST | `/api/admin/cluster-events` | 触发 AI 事件聚类 |
| GET | `/api/events` | 事件列表（二期） |

## 项目结构

```
john-readhub/
├── backend/          # FastAPI + APScheduler + SQLite
├── frontend/         # Next.js 15 + Tailwind
├── docker-compose.yml
└── README.md
```

## 扩展数据源

编辑 `backend/app/data/sources.seed.json` 添加 RSS 或 API 源，重启后端自动种子入库。

## 招聘爬虫（BOSS直聘 / 拉勾 / 脉脉 / 猎聘）

使用 Playwright 定向采集，职位归入 **招聘** 分类。

| 平台 | 默认方式 | 说明 |
|------|----------|------|
| 猎聘 | 开箱可用 | Playwright 拦截官方搜索 API |
| BOSS直聘 | 需 Cookie | 反爬强，建议配置 `SCRAPER_BOSS_COOKIE` |
| 拉勾 | 需 Cookie | WAF 拦截，建议配置 `SCRAPER_LAGOU_COOKIE` |
| 脉脉 | 需 Cookie | 职位需登录态，配置 `SCRAPER_MAIMAI_COOKIE` |

### 安装 Playwright 浏览器

```bash
cd backend && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 配置 Cookie（BOSS / 拉勾 / 脉脉）

1. 浏览器登录对应网站
2. 开发者工具 → Network → 任选请求 → 复制 **Cookie** 请求头
3. 写入 `backend/.env`：

```env
SCRAPER_BOSS_COOKIE=__zp_stoken__=...; ...
SCRAPER_LAGOU_COOKIE=...
SCRAPER_MAIMAI_COOKIE=...
```

4. 重启后端，手动触发：`curl -X POST http://localhost:8001/api/admin/fetch`

爬虫默认每 **120 分钟** 运行一次（`SCRAPER_FETCH_INTERVAL_MINUTES`），比 RSS 更低频，降低封禁风险。

关键词、城市等可在 `backend/app/data/sources.seed.json` 各爬虫的 `keywords` / `city` 字段调整。
