# QQ Music Cookie Manager

QQ音乐客户端Cookie抓取工具，专为 [Meting-API](https://github.com/mikus-loli/Meting-API) 优化。

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

## API接口

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/` | 否 | 服务状态 |
| GET | `/health` | 否 | 健康检查 |
| GET | `/api/meting` | 是 | 获取完整Cookie |
| GET | `/api/meting/simple` | 是 | 获取简化Cookie |

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

**简化格式** `GET /api/meting/simple`：
```json
{
  "success": true,
  "cookie": "uin=3166326944; qqmusic_key=Q_H_L_63k3..."
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

### 认证方式

使用 Meting-API 的认证头：
```
X-Auth-Username: admin
X-Auth-Token: your_token
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
