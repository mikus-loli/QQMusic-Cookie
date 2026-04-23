# QQ Music Cookie Manager 完整使用教程

## 目录

1. [产品介绍](#1-产品介绍)
2. [系统要求与环境准备](#2-系统要求与环境准备)
3. [安装配置详解](#3-安装配置详解)
4. [核心功能操作指南](#4-核心功能操作指南)
5. [常见应用场景](#5-常见应用场景)
6. [高级功能使用](#6-高级功能使用)
7. [故障排除指南](#7-故障排除指南)
8. [最佳实践建议](#8-最佳实践建议)

---

## 1. 产品介绍

### 1.1 什么是 QQ Music Cookie Manager？

QQ Music Cookie Manager 是一个专门用于抓取和管理QQ音乐客户端Cookie的工具。它通过MITM（中间人代理）技术捕获QQ音乐客户端的网络请求，提取其中的Cookie信息，并提供API接口和定时任务功能，方便将Cookie发送到其他项目或服务。

### 1.2 核心功能

| 功能模块 | 说明 |
|---------|------|
| **代理抓包** | 通过MITM代理捕获QQ音乐客户端的HTTPS请求 |
| **Cookie存储** | 自动解析并持久化存储Cookie到本地JSON文件 |
| **REST API** | 提供完整的HTTP API用于查询、创建、更新、删除Cookie |
| **定时发送** | 每天定时将Cookie发送到指定的目标API |
| **多运行模式** | 支持完整服务、仅API、仅代理等多种运行模式 |

### 1.3 工作原理

```
┌─────────────────────────────────────────────────────────────────┐
│                        工作流程图                                │
└─────────────────────────────────────────────────────────────────┘

  ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
  │ QQ音乐客户端  │───────▶│  MITM代理     │───────▶│  QQ音乐服务器 │
  │ (已登录状态)  │◀───────│ (127.0.0.1    │◀───────│              │
  └──────────────┘        │   :8080)      │        └──────────────┘
                          └───────┬───────┘
                                  │ 拦截请求
                                  ▼
                          ┌──────────────┐
                          │ Cookie提取    │
                          │ 解析Cookie头  │
                          └───────┬──────┘
                                  │ 存储
                                  ▼
                          ┌──────────────┐        ┌──────────────┐
                          │ Cookie存储    │───────▶│ cookies.json │
                          │ (内存+文件)   │        │ (持久化)      │
                          └───────┬──────┘        └──────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
          ┌──────────────┐            ┌──────────────┐
          │ REST API     │            │ 定时任务      │
          │ 查询/管理     │            │ 每天发送      │
          └──────────────┘            └───────┬──────┘
                                              │
                                              ▼
                                      ┌──────────────┐
                                      │ 目标API服务   │
                                      │ (您的项目)    │
                                      └──────────────┘
```

### 1.4 适用场景

- 自动化获取QQ音乐登录状态Cookie
- 为其他项目提供QQ音乐API访问所需的认证信息
- 定时同步Cookie到远程服务
- 多项目共享QQ音乐登录状态

---

## 2. 系统要求与环境准备

### 2.1 系统要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows 10/11、Linux、macOS |
| Python版本 | Python 3.9 或更高版本 |
| 内存 | 至少 512MB 可用内存 |
| 磁盘空间 | 至少 100MB 可用空间 |

### 2.2 检查Python环境

打开命令行终端，执行以下命令检查Python版本：

```bash
# Windows (PowerShell)
python --version

# Linux/macOS
python3 --version
```

预期输出：
```
Python 3.9.x 或更高版本
```

如果未安装Python或版本过低，请访问 [Python官网](https://www.python.org/downloads/) 下载安装。

### 2.3 确保pip可用

```bash
# 检查pip
pip --version

# 如果pip不可用，使用以下命令安装
python -m ensurepip --upgrade
```

---

## 3. 安装配置详解

### 3.1 获取项目代码

如果项目在Git仓库中：
```bash
git clone <repository-url>
cd QQMusic-Cookie
```

如果已有项目文件夹，直接进入：
```bash
cd d:\miku\QQMusic-Cookie
```

### 3.2 创建虚拟环境（推荐）

使用虚拟环境可以隔离项目依赖，避免与其他项目冲突：

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Windows CMD:
.\venv\Scripts\activate.bat

# Linux/macOS:
source venv/bin/activate
```

激活后，命令行前会显示 `(venv)` 标识。

### 3.3 安装依赖

```bash
pip install -r requirements.txt
```

依赖包说明：

| 包名 | 版本 | 用途 |
|------|------|------|
| mitmproxy | 10.1.6 | MITM代理核心 |
| fastapi | 0.109.0 | Web API框架 |
| uvicorn | 0.27.0 | ASGI服务器 |
| apscheduler | 3.10.4 | 定时任务调度 |
| pydantic | 2.5.3 | 数据验证 |
| httpx | 0.26.0 | HTTP客户端 |
| python-dotenv | 1.0.0 | 环境变量管理 |

### 3.4 配置环境变量

#### 3.4.1 复制配置模板

```bash
# 复制示例配置文件
copy .env.example .env    # Windows
cp .env.example .env      # Linux/macOS
```

#### 3.4.2 编辑配置文件

打开 `.env` 文件，根据需要修改配置：

```ini
# ============================================
# 基础配置
# ============================================

# 调试模式（生产环境设为false）
DEBUG=false

# ============================================
# 代理服务器配置
# ============================================

# MITM代理监听地址
PROXY_HOST=127.0.0.1

# MITM代理监听端口
PROXY_PORT=8080

# ============================================
# API服务配置
# ============================================

# API服务监听地址（0.0.0.0表示所有网卡）
API_HOST=0.0.0.0

# API服务端口
API_PORT=5000

# ============================================
# 定时任务配置
# ============================================

# 每天发送Cookie的时间（24小时制）
SCHEDULE_HOUR=8
SCHEDULE_MINUTE=0

# ============================================
# 目标API配置（接收Cookie的服务）
# ============================================

# 目标API地址（必填，否则定时发送无效）
TARGET_API_URL=http://your-server.com/api/cookies

# 认证Token（可选，根据目标API要求填写）
TARGET_API_TOKEN=your_secret_token_here
```

### 3.5 安装MITM代理证书

**这是最关键的一步！** 没有正确安装证书，代理无法解密HTTPS流量。

#### 3.5.1 启动代理服务

```bash
python main.py --proxy-only
```

#### 3.5.2 获取证书

保持代理运行，打开浏览器访问：

```
http://mitm.it
```

页面会显示不同操作系统的证书下载链接：

| 系统 | 证书文件 |
|------|---------|
| Windows | mitmproxy-ca-cert.p12 |
| macOS | mitmproxy-ca-cert.pem |
| Linux | mitmproxy-ca-cert.pem |
| Android | mitmproxy-ca-cert.cer |
| iOS | mitmproxy-ca-cert.pem |

#### 3.5.3 安装证书（Windows）

1. 下载 `mitmproxy-ca-cert.p12` 文件
2. 双击证书文件
3. 选择"当前用户"或"本地计算机"，点击"下一步"
4. 文件路径自动填充，点击"下一步"
5. 选择"将所有的证书都放入下列存储"
6. 点击"浏览"，选择"受信任的根证书颁发机构"
7. 点击"确定" → "下一步" → "完成"
8. 弹出安全警告，点击"是"确认安装

#### 3.5.4 验证证书安装

```bash
# Windows PowerShell
certutil -store -user Root | findstr mitmproxy

# 应该看到类似输出：
# ================ 证书 0 ================
# ...mitmproxy...
```

### 3.6 配置QQ音乐客户端代理

#### 方法一：系统代理（简单但影响全局）

1. 打开 Windows 设置
2. 进入"网络和Internet" → "代理"
3. 开启"使用代理服务器"
4. 地址填写：`127.0.0.1`
5. 端口填写：`8080`
6. 保存设置

#### 方法二：使用Proxifier（推荐，仅代理QQ音乐）

Proxifier 可以强制指定程序走代理，不影响其他应用。

1. 下载安装 [Proxifier](https://www.proxifier.com/)
2. 添加代理服务器：
   - 地址：`127.0.0.1`
   - 端口：`8080`
   - 协议：HTTPS
3. 添加代理规则：
   - 应用程序：选择QQ音乐可执行文件
   - 目标：选择刚才添加的代理服务器
   - 动作：Proxy

QQ音乐客户端可执行文件通常位于：
```
C:\Program Files (x86)\Tencent\QQMusic\QQMusic.exe
```

---

## 4. 核心功能操作指南

### 4.1 启动服务

#### 4.1.1 完整服务模式（推荐）

同时启动代理抓包、API服务和定时任务：

```bash
python main.py
```

输出示例：
```
==================================================
QQ Music Cookie Manager - Full Service Mode
==================================================
[Manager] API server started on http://0.0.0.0:5000
[Manager] Scheduler started - daily task at 08:00
[Manager] Starting proxy on 127.0.0.1:8080
[Manager] Please configure QQ Music client to use this proxy
[Manager] Press Ctrl+C to stop
[Proxy] Starting MITM proxy on 127.0.0.1:8080
[Proxy] Monitoring domains: ['y.qq.com', 'c.y.qq.com', ...]
```

#### 4.1.2 仅API服务模式

只运行API服务，不启动代理：

```bash
python main.py --api-only
```

适用场景：
- 只需要查询已存储的Cookie
- Cookie已抓取完成，只需要定时发送功能

#### 4.1.3 仅代理抓包模式

只运行代理抓包，不启动API服务：

```bash
python main.py --proxy-only
```

适用场景：
- 只需要抓取Cookie，不需要API查询
- 资源受限环境

### 4.2 抓取Cookie

#### 4.2.1 启动代理服务

```bash
python main.py
```

#### 4.2.2 配置QQ音乐客户端代理

确保QQ音乐客户端已配置使用代理 `127.0.0.1:8080`

#### 4.2.3 登录QQ音乐

1. 打开QQ音乐客户端
2. 登录您的QQ或微信账号
3. 浏览一些页面（如"我的音乐"、"歌单"等）

#### 4.2.4 验证抓取结果

代理终端会显示抓取日志：
```
[QQ Music] Captured cookies from y.qq.com
[Manager] Auto-saved 15 cookies from y.qq.com
```

查看存储的Cookie：
```bash
python main.py --status
```

输出示例：
```
Cookie Status:
  Total hosts: 3
  Total cookies: 45

  [y.qq.com]
    Captured: 2024-01-15T10:30:00.000000
    Updated: 2024-01-15T10:35:00.000000
    Cookies: 20

  [c.y.qq.com]
    Captured: 2024-01-15T10:31:00.000000
    Updated: 2024-01-15T10:31:00.000000
    Cookies: 15

  [u.y.qq.com]
    Captured: 2024-01-15T10:32:00.000000
    Updated: 2024-01-15T10:32:00.000000
    Cookies: 10
```

### 4.3 使用API接口

#### 4.3.1 获取服务状态

```bash
curl http://localhost:5000/
```

响应：
```json
{
  "status": "running",
  "timestamp": "2024-01-15T10:30:00.000000",
  "total_hosts": 3,
  "total_cookies": 45
}
```

#### 4.3.2 获取所有Cookie

```bash
curl http://localhost:5000/api/cookies
```

响应：
```json
{
  "success": true,
  "message": "Found 3 hosts with cookies",
  "data": {
    "y.qq.com": {
      "cookies": {
        "uin": "123456789",
        "skey": "abcdef123456",
        "p_skey": "xyz789",
        "qqmusic_key": "music_key_value"
      },
      "source_host": "y.qq.com",
      "captured_at": "2024-01-15T10:30:00.000000",
      "updated_at": "2024-01-15T10:35:00.000000"
    }
  }
}
```

#### 4.3.3 获取指定主机的Cookie

```bash
curl http://localhost:5000/api/cookies/y.qq.com
```

#### 4.3.4 获取Cookie字符串格式

```bash
curl http://localhost:5000/api/cookies/string
```

响应：
```json
{
  "success": true,
  "cookie_string": "uin=123456789; skey=abcdef123456; p_skey=xyz789; qqmusic_key=music_key_value",
  "source_host": null
}
```

#### 4.3.5 手动添加Cookie

```bash
curl -X POST http://localhost:5000/api/cookies \
  -H "Content-Type: application/json" \
  -d '{
    "source_host": "y.qq.com",
    "cookies": {
      "uin": "123456789",
      "skey": "new_skey_value"
    }
  }'
```

#### 4.3.6 更新Cookie

```bash
curl -X PUT http://localhost:5000/api/cookies/y.qq.com \
  -H "Content-Type: application/json" \
  -d '{
    "cookies": {
      "new_cookie_name": "new_cookie_value"
    }
  }'
```

#### 4.3.7 删除指定主机的Cookie

```bash
curl -X DELETE http://localhost:5000/api/cookies/y.qq.com
```

#### 4.3.8 清空所有Cookie

```bash
curl -X DELETE http://localhost:5000/api/cookies
```

### 4.4 定时发送Cookie

#### 4.4.1 配置目标API

编辑 `.env` 文件：

```ini
TARGET_API_URL=http://your-server.com/api/receive-cookies
TARGET_API_TOKEN=your_auth_token
```

#### 4.4.2 设置发送时间

```ini
SCHEDULE_HOUR=8    # 每天8点
SCHEDULE_MINUTE=0  # 0分
```

#### 4.4.3 启动服务

```bash
python main.py
```

定时任务会自动在指定时间发送Cookie。

#### 4.4.4 手动触发发送

```bash
python main.py --send-now
```

输出：
```
[Scheduler] Running scheduled task at 2024-01-15T10:40:00.000000
[Scheduler] Successfully sent 45 cookies to http://your-server.com/api/receive-cookies
[Scheduler] Task result: {'success': True, 'cookies_sent': 45, 'response_status': 200}
```

---

## 5. 常见应用场景

### 5.1 场景一：为自动化脚本提供Cookie

**需求**：您有一个自动化脚本需要使用QQ音乐API，需要登录态Cookie。

**解决方案**：

1. 启动Cookie Manager抓取Cookie
2. 脚本通过API获取Cookie

```python
import requests

# 从Cookie Manager获取Cookie
response = requests.get('http://localhost:5000/api/cookies/string')
cookie_string = response.json()['cookie_string']

# 使用Cookie访问QQ音乐API
headers = {
    'Cookie': cookie_string,
    'User-Agent': 'Mozilla/5.0 ...'
}

api_response = requests.get(
    'https://c.y.qq.com/v8/fcg-bin/fcg_v8_toplist_cp.fcg',
    headers=headers
)

print(api_response.json())
```

### 5.2 场景二：定时同步Cookie到远程服务器

**需求**：您有一个远程服务需要定期获取最新的QQ音乐Cookie。

**解决方案**：

1. 配置目标API地址
2. 启动完整服务模式
3. 系统每天定时发送

远程服务器接收端示例（Python Flask）：

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/receive-cookies', methods=['POST'])
def receive_cookies():
    auth_header = request.headers.get('Authorization')
    
    # 验证Token
    if auth_header != 'Bearer your_secret_token_here':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    cookies = data.get('cookies', {})
    cookie_string = data.get('cookie_string', '')
    
    # 存储或使用Cookie
    print(f"Received {len(cookies)} cookies")
    print(f"Cookie string: {cookie_string}")
    
    # 可以存储到数据库或缓存
    # redis.set('qqmusic_cookies', cookie_string)
    
    return jsonify({'success': True, 'received': len(cookies)})

if __name__ == '__main__':
    app.run(port=8000)
```

### 5.3 场景三：多项目共享Cookie

**需求**：多个项目都需要使用QQ音乐Cookie，希望统一管理。

**解决方案**：

1. Cookie Manager作为中心服务运行
2. 各项目通过API获取Cookie

架构图：
```
                    ┌──────────────────┐
                    │  Cookie Manager  │
                    │  (API:5000)      │
                    └────────┬─────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
           ▼                 ▼                 ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │   项目 A      │  │   项目 B      │  │   项目 C      │
    │ (爬虫脚本)    │  │ (API服务)     │  │ (定时任务)    │
    └──────────────┘  └──────────────┘  └──────────────┘
```

各项目获取Cookie的代码：

```python
import httpx

async def get_qqmusic_cookie():
    async with httpx.AsyncClient() as client:
        response = await client.get('http://localhost:5000/api/cookies/string')
        return response.json()['cookie_string']

# 使用示例
cookie = await get_qqmusic_cookie()
```

### 5.4 场景四：Docker部署

**Dockerfile示例**：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 创建数据目录
RUN mkdir -p /app/data

EXPOSE 5000 8080

CMD ["python", "main.py"]
```

**docker-compose.yml示例**：

```yaml
version: '3.8'

services:
  qqmusic-cookie:
    build: .
    container_name: qqmusic-cookie-manager
    ports:
      - "5000:5000"
      - "8080:8080"
    volumes:
      - ./data:/app/data
      - ./mitmproxy-cert:/root/.mitmproxy
    environment:
      - TARGET_API_URL=http://your-server.com/api/cookies
      - TARGET_API_TOKEN=your_token
      - SCHEDULE_HOUR=8
      - SCHEDULE_MINUTE=0
    restart: unless-stopped
```

启动：
```bash
docker-compose up -d
```

---

## 6. 高级功能使用

### 6.1 自定义监控域名

如果需要监控其他QQ音乐相关域名，修改 `config.py`：

```python
QQ_MUSIC_DOMAINS: list = [
    "y.qq.com",
    "c.y.qq.com",
    "u.y.qq.com",
    "m.y.qq.com",
    "api.y.qq.com",
    # 添加自定义域名
    "other.qq.com",
]
```

### 6.2 自定义定时任务

除了每日定时发送，可以添加自定义定时任务：

```python
from scheduler import scheduler_manager

# 添加每6小时执行的任务
scheduler_manager.add_custom_schedule(
    job_id="every_6_hours",
    cron_expression="0 */6 * * *",  # 每6小时
    job_func=your_custom_function
)
```

Cron表达式说明：
```
┌───────────── 分钟 (0 - 59)
│ ┌───────────── 小时 (0 - 23)
│ │ ┌───────────── 日 (1 - 31)
│ │ │ ┌───────────── 月 (1 - 12)
│ │ │ │ ┌───────────── 星期 (0 - 6, 0=周日)
│ │ │ │ │
* * * * *
```

常用表达式：
| 表达式 | 说明 |
|--------|------|
| `0 8 * * *` | 每天8:00 |
| `0 */6 * * *` | 每6小时 |
| `0 0 * * 0` | 每周日0:00 |
| `0 9-17 * * 1-5` | 周一到周五9:00-17:00每小时 |

### 6.3 修改目标API数据格式

如果目标API需要不同的数据格式，修改 `scheduler.py` 中的 `send_cookies_to_target` 方法：

```python
async def send_cookies_to_target(self) -> dict:
    # ... 现有代码 ...
    
    # 自定义数据格式
    payload = {
        "auth": {
            "cookies": cookies,
            "cookie_header": cookie_store.get_cookie_string()
        },
        "metadata": {
            "source": "qqmusic",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0"
        }
    }
    
    # ... 发送代码 ...
```

### 6.4 添加Webhook通知

在Cookie更新或发送失败时发送通知：

```python
# 在 scheduler.py 中添加
import httpx

async def send_notification(webhook_url: str, message: str):
    async with httpx.AsyncClient() as client:
        await client.post(webhook_url, json={"content": message})

# 在发送失败时调用
async def send_cookies_to_target(self) -> dict:
    try:
        # ... 发送逻辑 ...
    except Exception as e:
        await send_notification(
            "https://your-webhook-url",
            f"QQ Music Cookie发送失败: {str(e)}"
        )
        return {"success": False, "error": str(e)}
```

### 6.5 数据备份与恢复

#### 备份Cookie数据

```bash
# 手动备份
copy data\cookies.json data\cookies_backup_20240115.json

# 定时备份脚本 (backup.py)
import shutil
from datetime import datetime
from pathlib import Path

def backup_cookies():
    src = Path("data/cookies.json")
    if src.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dst = Path(f"data/backups/cookies_{timestamp}.json")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)
        print(f"Backup created: {dst}")

if __name__ == "__main__":
    backup_cookies()
```

#### 恢复Cookie数据

```bash
# 恢复指定备份
copy data\backups\cookies_20240115_080000.json data\cookies.json
```

---

## 7. 故障排除指南

### 7.1 常见问题与解决方案

#### 问题1：无法抓取到Cookie

**症状**：代理运行正常，但Cookie列表为空

**排查步骤**：

1. **检查代理配置**
   ```bash
   # 确认代理正在运行
   netstat -an | findstr 8080
   ```

2. **检查证书安装**
   ```bash
   # Windows检查证书
   certutil -store -user Root | findstr mitmproxy
   ```

3. **检查QQ音乐是否走代理**
   - 打开QQ音乐客户端
   - 访问任意页面
   - 查看代理终端是否有日志输出

4. **解决方案**：
   - 重新安装MITM证书到"受信任的根证书颁发机构"
   - 使用Proxifier强制QQ音乐走代理
   - 检查是否有其他代理软件冲突

#### 问题2：HTTPS解密失败

**症状**：代理日志显示SSL错误

**解决方案**：

```bash
# 清除现有证书
rmdir /s /q %USERPROFILE%\.mitmproxy

# 重新启动代理，会生成新证书
python main.py --proxy-only

# 重新下载安装证书
# 访问 http://mitm.it
```

#### 问题3：定时任务未执行

**症状**：到达设定时间但Cookie未发送

**排查步骤**：

1. **检查配置**
   ```bash
   # 查看.env配置
   type .env | findstr SCHEDULE
   type .env | findstr TARGET_API
   ```

2. **检查目标API是否配置**
   - `TARGET_API_URL` 必须填写
   - URL必须以 `http://` 或 `https://` 开头

3. **手动测试发送**
   ```bash
   python main.py --send-now
   ```

4. **检查调度器状态**
   ```python
   # 在Python中检查
   from scheduler import scheduler_manager
   print(scheduler_manager.get_status())
   ```

#### 问题4：API服务无法访问

**症状**：curl请求超时或拒绝连接

**排查步骤**：

1. **检查服务是否运行**
   ```bash
   netstat -an | findstr 5000
   ```

2. **检查防火墙**
   ```bash
   # Windows防火墙规则
   netsh advfirewall firewall show rule name=all | findstr 5000
   ```

3. **解决方案**：
   ```bash
   # 添加防火墙规则
   netsh advfirewall firewall add rule name="QQMusic Cookie API" dir=in action=allow protocol=tcp localport=5000
   ```

#### 问题5：Cookie存储文件损坏

**症状**：启动时报JSON解析错误

**解决方案**：

1. **检查文件内容**
   ```bash
   type data\cookies.json
   ```

2. **手动修复或删除**
   ```bash
   # 删除损坏文件（会丢失已存储的Cookie）
   del data\cookies.json
   
   # 或从备份恢复
   copy data\backups\cookies_latest.json data\cookies.json
   ```

### 7.2 日志分析

#### 启用调试模式

修改 `.env`：
```ini
DEBUG=true
```

#### 查看详细日志

```bash
# 启动时添加详细输出
python main.py 2>&1 | tee app.log
```

#### 关键日志信息

| 日志内容 | 含义 |
|---------|------|
| `[Proxy] Starting MITM proxy` | 代理启动成功 |
| `[QQ Music] Captured cookies from xxx` | 成功抓取Cookie |
| `[Store] Saved N cookies from xxx` | Cookie存储成功 |
| `[Scheduler] Successfully sent N cookies` | 定时发送成功 |
| `[Scheduler] Job error: xxx` | 定时任务错误 |
| `SSL handshake failed` | SSL证书问题 |

### 7.3 性能问题排查

#### 内存占用过高

**原因**：大量请求缓存

**解决方案**：
- 定期重启服务
- 限制抓取的域名范围

#### CPU占用过高

**原因**：代理处理大量请求

**解决方案**：
- 使用 `--api-only` 模式，仅在需要抓取时启动代理
- 配置QQ音乐客户端直连，仅登录时使用代理

---

## 8. 最佳实践建议

### 8.1 安全建议

1. **保护Cookie数据**
   - Cookie文件包含敏感登录信息，不要分享或上传到公开仓库
   - 添加到 `.gitignore`：
     ```
     data/
     .env
     *.json
     ```

2. **API访问控制**
   - 生产环境中添加API认证
   - 使用HTTPS而非HTTP
   - 限制API访问IP范围

3. **Token管理**
   - 定期更换 `TARGET_API_TOKEN`
   - 使用强随机Token

### 8.2 可靠性建议

1. **定时任务容错**
   - 系统已配置 `misfire_grace_time=3600`
   - 如果错过执行时间，会在1小时内补执行

2. **数据持久化**
   - Cookie自动保存到文件
   - 建议定期备份 `data/cookies.json`

3. **服务监控**
   ```python
   # 添加健康检查脚本
   import requests
   
   def health_check():
       try:
           response = requests.get('http://localhost:5000/health', timeout=5)
           return response.status_code == 200
       except:
           return False
   
   # 可以配合cron定时检查并自动重启
   ```

### 8.3 使用流程建议

**推荐的使用流程**：

```
1. 首次部署
   └─ 安装依赖 → 配置环境 → 安装证书 → 测试抓取

2. 日常使用
   └─ 启动服务 → 登录QQ音乐 → 验证抓取 → 确认定时任务

3. 维护
   └─ 定期检查日志 → 备份数据 → 更新Token
```

### 8.4 常用命令速查

```bash
# 安装依赖
pip install -r requirements.txt

# 完整服务
python main.py

# 仅API
python main.py --api-only

# 仅代理
python main.py --proxy-only

# 查看状态
python main.py --status

# 立即发送
python main.py --send-now

# 指定端口
python main.py --port 6000

# 查看帮助
python main.py --help
```

### 8.5 API速查表

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/` | 服务状态 |
| GET | `/health` | 健康检查 |
| GET | `/api/cookies` | 获取所有Cookie |
| GET | `/api/cookies/{host}` | 获取指定主机Cookie |
| GET | `/api/cookies/string` | 获取Cookie字符串 |
| POST | `/api/cookies` | 创建Cookie记录 |
| PUT | `/api/cookies/{host}` | 更新Cookie |
| DELETE | `/api/cookies/{host}` | 删除指定Cookie |
| DELETE | `/api/cookies` | 清空所有Cookie |

---

## 附录

### A. QQ音乐常见Cookie字段说明

| 字段名 | 说明 |
|--------|------|
| `uin` | 用户QQ号 |
| `skey` | 会话密钥 |
| `p_skey` | 支付相关密钥 |
| `qqmusic_key` | 音乐服务密钥 |
| `wxuin` | 微信用户ID（微信登录时） |
| `pass_ticket` | 登录票据 |

### B. 相关资源

- [mitmproxy官方文档](https://docs.mitmproxy.org/)
- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [APScheduler文档](https://apscheduler.readthedocs.io/)
- [Python httpx文档](https://www.python-httpx.org/)

### C. 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| 1.0.0 | 2024-01-15 | 初始版本 |

---

如有问题或建议，欢迎提交Issue或Pull Request。
