# QQ Music Cookie Manager

QQ音乐客户端Cookie抓取工具，专为 [Meting-API](https://github.com/mikus-loli/Meting-API) 优化。

## 功能特性

- 🎵 **Cookie抓取**：通过MITM代理自动抓取QQ音乐客户端Cookie
- 🎨 **管理后台**：现代化响应式Web管理界面
- 🔐 **安全认证**：Token认证保护API访问
- ⏰ **定时同步**：自动定时发送Cookie到Meting-API
- 🔄 **自动续期**：支持refresh_token自动续期
- 🤖 **全自动化**：自动启动QQ音乐、抓取、发送、关闭的完整流程

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
# API安全Token
API_TOKEN=your_secure_token_here

# Meting-API 配置
TARGET_API_URL=http://localhost:3000/admin/cookies
TARGET_API_TOKEN=mapi_xxxxxxxx...

# QQ音乐路径（可选，自动检测）
QQMUSIC_PATH=C:\Program Files (x86)\Tencent\QQMusic\QQMusic.exe
```

### 3. 安装MITM证书

```bash
# 启动代理后访问
http://mitm.it

# Windows安装证书到"受信任的根证书颁发机构"
```

## 运行模式

### 自动化模式（推荐）

全自动循环：启动QQ音乐 → 抓取Cookie → 发送 → 关闭 → 等待 → 循环

```bash
# 双击运行
run_automate.bat

# 或命令行
python automate.py --interval 24
```

**参数说明**：
- `--interval 24`：每24小时执行一次
- `--once`：仅执行一次

### 手动模式

```bash
# 完整服务（代理+API+定时任务）
python main.py

# 仅API服务
python main.py --api-only

# 仅代理抓包
python main.py --proxy-only

# 立即发送Cookie
python main.py --send-now

# 查看状态
python main.py --status
```

## 自动化流程

```
┌─────────────────────────────────────────────────────────────┐
│                    自动化流程 (每24小时)                      │
└─────────────────────────────────────────────────────────────┘

  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
  │  启动代理     │────▶│  启动QQ音乐   │────▶│  等待Cookie  │
  └──────────────┘     └──────────────┘     └───────┬──────┘
                                                     │
        ┌────────────────────────────────────────────┘
        ▼
  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
  │  发送Cookie   │────▶│  关闭QQ音乐   │────▶│  清理文件    │
  └──────────────┘     └──────────────┘     └───────┬──────┘
                                                     │
        ┌────────────────────────────────────────────┘
        ▼
  ┌──────────────┐
  │  等待24小时   │
  └───────┬──────┘
          │
          └──────────────────────▶ 循环
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

## API接口

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/` | 否 | 服务状态 |
| GET | `/health` | 否 | 健康检查 |
| GET | `/api/meting` | 是 | 获取完整Cookie |
| GET | `/api/meting/simple` | 是 | 获取简化Cookie |
| POST | `/api/cookies` | 是 | 添加Cookie |
| POST | `/api/send` | 是 | 发送Cookie到Meting-API |
| DELETE | `/api/cookies` | 是 | 清空所有Cookie |

### 认证方式

所有 `/api/meting` 端点需要 Bearer Token 认证：

```bash
curl -H "Authorization: Bearer your_token" http://localhost:5000/api/meting
```

## 定时同步到Meting-API

### 配置说明

| 变量 | 说明 |
|------|------|
| `TARGET_API_URL` | Meting-API Cookie接口地址 |
| `TARGET_API_TOKEN` | Meting-API Token（以 `mapi_` 开头） |
| `QQMUSIC_PATH` | QQ音乐可执行文件路径（可选） |

### 发送数据格式

```json
{
  "platform": "tencent",
  "cookie": "uin=3166326944; qqmusic_key=Q_H_L_63k3...; psrf_qqrefresh_token=...",
  "note": "Auto-synced from QQMusic-Cookie-Manager",
  "isActive": true
}
```

## Cookie 格式说明

**QQ音乐最简格式**：
```
uin=你的QQ号; qqmusic_key=Q_H_L_开头的key
```

**完整格式（支持自动续期）**：
```
uin=你的QQ号; qqmusic_key=Q_H_L_xxx; qm_keyst=Q_H_L_xxx; psrf_qqrefresh_token=刷新token
```

## 项目结构

```
QQMusic-Cookie/
├── automate.py          # 自动化脚本
├── main.py              # 主程序入口
├── config.py            # 配置管理
├── api_server.py        # REST API服务
├── proxy_capture.py     # MITM代理抓包
├── cookie_store.py      # Cookie存储
├── scheduler.py         # 定时任务
├── run_automate.bat     # 自动化启动脚本
├── run_once.bat         # 单次执行脚本
├── static/              # 前端静态文件
├── data/                # 数据目录
├── requirements.txt     # 完整依赖
└── .env.example         # 配置示例
```

## 安全建议

1. **设置API_TOKEN**：防止Cookie被未授权访问
2. **使用HTTPS**：生产环境建议配置反向代理
3. **限制访问IP**：通过防火墙限制API访问来源
4. **定期更换Token**：提高安全性

## 常见问题

### Q: 自动化模式无法启动QQ音乐？
A: 检查 `.env` 中的 `QQMUSIC_PATH` 是否正确，或确保QQ音乐安装在默认路径。

### Q: Cookie抓取失败？
A: 确保已安装MITM证书，并配置QQ音乐走代理。

### Q: 发送失败？
A: 检查 `TARGET_API_URL` 和 `TARGET_API_TOKEN` 配置是否正确。
