# qBT-Dashboard

> qBittorrent 多实例集中管理面板，支持定时强制做种、连接监控、多用户管理。

基于 **FastAPI** 开发的 qBittorrent WebUI 管理工具，可集中管理多个 qBittorrent 实例，为每个实例独立配置定时强制做种（Reannounce）策略，并通过 Web 面板统一监控状态。

---

## 功能特色

- **多实例管理** — 同时管理多个 qBittorrent 客户端，支持 4.x/5.x WebUI API v2
- **定时强制做种** — 为每个实例独立配置做种计划，自动按间隔执行 reannounce
- **连接监控** — 一键测试各实例连接状态，运行记录可追溯
- **安全认证** — 管理员账号密码登录，实例密码加密存储（Fernet）
- **实时执行** — 手动触发任意实例立即做种，无需等待定时任务
- **响应式界面** — 适配桌面与移动端的 Web 管理面板
- **Docker 支持** — 一键容器化部署

## 技术栈

| 层 | 技术 |
|------|------|
| 后端框架 | FastAPI + Uvicorn |
| 前端 | Jinja2 模板 + 原生 JS/CSS |
| 数据库 | SQLite（本地存储） |
| 定时任务 | APScheduler |
| 加密 | cryptography (Fernet) + bcrypt |
| HTTP 客户端 | httpx |
| 部署 | Docker / 裸机 |

## 快速开始

### 环境准备

```bash
python -m pip install -r requirements.txt
cp .env.example .env
```

编辑 `.env` 文件，填写必填配置（见下方环境变量说明）。

### 启动服务

**方式 1 — 启动脚本（推荐）**

```bash
# Windows
start.bat

# Linux / macOS
chmod +x start.sh && ./start.sh
```

**方式 2 — Python 启动器**

```bash
python run.py
python run.py --port 9000    # 自定义端口
python run.py --no-browser   # 不自动打开浏览器
```

**方式 3 — Uvicorn**

```bash
uvicorn app.main:app --reload
```

### Docker 部署

```bash
cp .env.example .env
# 编辑 .env 填写真实配置
docker compose up --build
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `APP_SECRET_KEY` | 面板会话签名密钥 | **（必填）** |
| `APP_ENCRYPTION_KEY` | qB 实例密码加密密钥，合法 Fernet key | **（必填）** |
| `BOOTSTRAP_ADMIN_USERNAME` | 初始管理员账号 | `admin` |
| `BOOTSTRAP_ADMIN_PASSWORD` | 初始管理员密码 | **（必填）** |
| `DATABASE_PATH` | SQLite 数据库路径 | 平台默认位置 |
| `SECURE_COOKIES` | 是否启用安全 Cookie | `false` |
| `SCHEDULER_ENABLED` | 是否启用定时任务 | `true` |

### 生成加密密钥

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/auth/login` | 管理员登录 |
| POST | `/auth/logout` | 登出 |
| GET | `/api/v1/summary` | 面板概览统计 |
| GET | `/api/v1/instances` | 获取实例列表 |
| POST | `/api/v1/instances` | 添加 qB 实例 |
| PATCH | `/api/v1/instances/{id}` | 更新实例配置 |
| POST | `/api/v1/instances/{id}/test-connection` | 测试实例连接 |
| POST | `/api/v1/instances/{id}/run-now` | 立即执行做种 |
| GET | `/api/v1/instances/{id}/runs` | 查看做种记录 |

## 数据存储

| 系统 | 默认路径 |
|------|----------|
| Windows | `%LOCALAPPDATA%\qb-panel\data\app.db` |
| Linux / macOS | `~/.local/share/qb-panel/data/app.db` |

## 跨平台支持

- **Windows** 10/11
- **Linux** (Ubuntu, Debian, CentOS 等)
- **macOS**
- **Docker**（任意宿主）

## 注意事项

- 定时任务为进程内调度，不支持多实例分布式部署
- 兼容 qBittorrent 4.x/5.x WebUI API v2，测试至 4.3.9
- 为兼容旧版，重新做种逻辑先获取全部种子 hash，再分批调用 reannounce
- 若 qB WebUI 使用自签名证书，可在实例配置中关闭 `verify_tls`
