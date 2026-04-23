# QQ Music Cookie Manager

QQ音乐客户端Cookie抓取和管理工具，支持定时发送到目标API。

> 📖 **完整教程**：请查看 [TUTORIAL.md](./TUTORIAL.md) 获取详细的安装配置、使用指南和故障排除方案。

## 项目结构

```
QQMusic-Cookie/
├── main.py              # 主程序入口
├── config.py            # 配置管理
├── proxy_capture.py     # MITM代理抓包模块
├── cookie_store.py      # Cookie存储管理
├── api_server.py        # REST API服务
├── scheduler.py         # 定时任务调度
├── requirements.txt     # Python依赖
├── .env.example         # 环境变量示例
└── data/
    └── cookies.json     # Cookie存储文件
```

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
# 目标API地址（接收Cookie的服务）
TARGET_API_URL=http://your-server.com/api/cookies
TARGET_API_TOKEN=your_token_here

# 定时发送时间（每天8:00）
SCHEDULE_HOUR=8
SCHEDULE_MINUTE=0
```

### 3. 安装MITM代理证书

首次使用需要安装mitmproxy的CA证书：

```bash
# 启动代理后访问
http://mitm.it

# 或直接安装证书文件
# Windows: %USERPROFILE%\.mitmproxy\mitmproxy-ca-cert.p12
```

### 4. 配置QQ音乐客户端代理

**方法一：系统代理**
- Windows设置 → 网络 → 代理 → 手动设置代理
- 地址：`127.0.0.1`，端口：`8080`

**方法二：Proxifier等工具强制代理QQ音乐进程**

## 运行模式

### 完整服务模式（推荐）

同时运行代理抓包、API服务和定时任务：

```bash
python main.py
```

### 仅API服务

只运行API服务（用于查询和管理已存储的Cookie）：

```bash
python main.py --api-only
```

### 仅代理抓包

只运行代理抓包功能：

```bash
python main.py --proxy-only
```

### 手动发送Cookie

立即发送Cookie到目标API：

```bash
python main.py --send-now
```

### 查看状态

查看当前存储的Cookie状态：

```bash
python main.py --status
```

## API接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 服务状态 |
| GET | `/api/cookies` | 获取所有Cookie |
| GET | `/api/cookies/{host}` | 获取指定主机的Cookie |
| GET | `/api/cookies/string` | 获取Cookie字符串格式 |
| POST | `/api/cookies` | 手动添加Cookie |
| PUT | `/api/cookies/{host}` | 更新指定主机的Cookie |
| DELETE | `/api/cookies/{host}` | 删除指定主机的Cookie |
| DELETE | `/api/cookies` | 清空所有Cookie |

### API使用示例

```bash
# 获取所有Cookie
curl http://localhost:5000/api/cookies

# 获取Cookie字符串
curl http://localhost:5000/api/cookies/string

# 手动添加Cookie
curl -X POST http://localhost:5000/api/cookies \
  -H "Content-Type: application/json" \
  -d '{"source_host": "y.qq.com", "cookies": {"uin": "123456", "skey": "abcdef"}}'
```

## 目标API数据格式

定时任务发送到目标API的数据格式：

```json
{
  "cookies": {
    "uin": "123456",
    "skey": "abcdef",
    "p_skey": "xyz123"
  },
  "cookie_string": "uin=123456; skey=abcdef; p_skey=xyz123",
  "timestamp": "2024-01-15T08:00:00.000000",
  "source": "qqmusic-cookie-manager"
}
```

## 注意事项

1. **证书信任**：必须信任mitmproxy的CA证书才能抓取HTTPS流量
2. **代理配置**：QQ音乐客户端需要配置使用代理
3. **登录状态**：确保QQ音乐客户端已登录，登录后会产生包含用户信息的Cookie
4. **定时任务**：如果错过执行时间，会在1小时内补执行（misfire_grace_time=3600）

## 工作流程

```
┌─────────────────┐
│ QQ音乐客户端登录 │
└────────┬────────┘
         │ HTTPS请求
         ▼
┌─────────────────┐
│  MITM代理抓包    │ ← 监听 127.0.0.1:8080
└────────┬────────┘
         │ 提取Cookie
         ▼
┌─────────────────┐
│  Cookie存储      │ ← 保存到 data/cookies.json
└────────┬────────┘
         │ 每天8:00定时
         ▼
┌─────────────────┐
│  发送到目标API   │ ← POST到 TARGET_API_URL
└─────────────────┘
```
