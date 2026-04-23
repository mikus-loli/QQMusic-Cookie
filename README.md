# QQ Music Cookie Manager

QQ音乐客户端Cookie抓取工具，专为 [Meting-API](https://github.com/mikus-loli/Meting-API) 优化。

## 功能特性

- 🎵 **Cookie抓取**：通过MITM代理自动抓取QQ音乐客户端Cookie
- 🎨 **管理后台**：现代化响应式Web管理界面
- 🔐 **安全认证**：Token认证保护API访问
- ⏰ **定时同步**：自动定时发送Cookie到Meting-API
- 🔄 **自动续期**：支持refresh_token自动续期

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```ini
# API安全Token（保护Cookie API不被未授权访问）
API_TOKEN=your_secure_token_here

# Meting-API 配置（定时同步Cookie）
TARGET_API_URL=http://localhost:3000/admin/cookies
TARGET_API_USERNAME=admin
TARGET_API_TOKEN=your_meting_api_token

# 定时发送时间
SCHEDULE_HOUR=8
SCHEDULE_MINUTE=0
```

### 3. 安装MITM证书

```bash
# 启动代理后访问
http://mitm.it

# Windows安装证书到"受信任的根证书颁发机构"
```

### 4. 配置QQ音乐代理

使用Proxifier强制QQ音乐走代理 `127.0.0.1:8080`

### 5. 启动服务

```bash
python main.py
```

## 管理后台

启动服务后访问 `http://localhost:5000/admin` 进入管理后台。

### 功能模块

| 模块 | 功能 |
|------|------|
| 仪表盘 | Cookie状态、统计信息、快速操作 |
| Cookie管理 | 查看、添加、删除Cookie |
| 定时任务 | 配置定时同步、手动触发 |
| 系统设置 | API配置、快速操作 |

### 登录

使用 `.env` 中配置的 `API_TOKEN` 登录管理后台。

## API接口

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/` | 否 | 服务状态 |
| GET | `/health` | 否 | 健康检查 |
| GET | `/api/meting` | 是 | 获取完整Cookie |
| GET | `/api/meting/simple` | 是 | 获取简化Cookie |
| POST | `/api/cookies` | 是 | 添加Cookie |
| DELETE | `/api/cookies` | 是 | 清空所有Cookie |

### 认证方式

所有 `/api/meting` 端点需要 Bearer Token 认证：

```bash
curl -H "Authorization: Bearer your_token" http://localhost:5000/api/meting
```

### 响应示例

**完整格式** `GET /api/meting`：
```json
{
  "success": true,
  "platform": "tencent",
  "uin": "3166326944",
  "qqmusic_key": "Q_H_L_63k3...",
  "cookie": "uin=3166326944; qqmusic_key=Q_H_L_63k3...; psrf_qqrefresh_token=...",
  "refresh_token": "7F6CEFEA...",
  "has_refresh_token": true
}
```

## 定时同步到Meting-API

### 配置说明

| 变量 | 说明 |
|------|------|
| `TARGET_API_URL` | Meting-API Cookie接口地址，如 `http://localhost:3000/admin/cookies` |
| `TARGET_API_USERNAME` | Meting-API 登录用户名 |
| `TARGET_API_TOKEN` | Meting-API 登录Token |

### 发送数据格式

```json
{
  "platform": "tencent",
  "cookie": "uin=3166326944; qqmusic_key=Q_H_L_63k3...; psrf_qqrefresh_token=...",
  "remark": "Auto-synced from QQMusic-Cookie-Manager at 2024-01-15 08:00"
}
```

## 运行模式

```bash
# 完整服务（代理+API+定时任务）
python main.py

# 仅API服务
python main.py --api-only

# 仅代理抓包
python main.py --proxy-only

# 立即发送Cookie到Meting-API
python main.py --send-now

# 查看状态
python main.py --status
```

## 项目结构

```
QQMusic-Cookie/
├── main.py              # 主程序入口
├── config.py            # 配置管理
├── api_server.py        # REST API服务
├── proxy_capture.py     # MITM代理抓包
├── cookie_store.py      # Cookie存储
├── scheduler.py         # 定时任务
├── static/              # 前端静态文件
│   ├── index.html       # 管理后台
│   ├── css/
│   │   ├── style.css
│   │   └── responsive.css
│   └── js/
│       └── auth.js
├── data/                # 数据目录
│   └── cookies.json     # Cookie存储
├── requirements.txt     # 完整依赖
├── requirements-lite.txt # 轻量依赖
└── .env.example         # 配置示例
```

## 安全建议

1. **设置API_TOKEN**：防止Cookie被未授权访问
2. **使用HTTPS**：生产环境建议配置反向代理
3. **限制访问IP**：通过防火墙限制API访问来源
4. **定期更换Token**：提高安全性

## 工作流程

```
QQ音乐客户端 → MITM代理(8080) → Cookie存储 → API服务(5000)
                                    ↓
                            定时同步到Meting-API
```
