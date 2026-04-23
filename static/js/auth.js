const API_BASE = '';
let authToken = localStorage.getItem('authToken');

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer') || createToastContainer();
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <svg viewBox="0 0 24 24" width="20" height="20">
            ${getToastIcon(type)}
        </svg>
        <span>${message}</span>
    `;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

function getToastIcon(type) {
    switch(type) {
        case 'success':
            return '<path d="M20 6L9 17l-5-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>';
        case 'error':
            return '<circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/><path d="M15 9l-6 6M9 9l6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>';
        case 'warning':
            return '<path d="M12 9v4M12 17h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>';
        default:
            return '<circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 16v-4M12 8h.01" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>';
    }
}

async function apiRequest(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers
        });
        
        if (response.status === 401) {
            logout();
            throw new Error('Unauthorized');
        }
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Request failed' }));
            throw new Error(error.detail || 'Request failed');
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

function checkAuth() {
    if (!authToken) {
        showLoginPage();
        return false;
    }
    return true;
}

function showLoginPage() {
    document.body.innerHTML = `
    <div class="login-container">
        <div class="login-card">
            <div class="login-header">
                <div class="logo">
                    <svg viewBox="0 0 24 24" width="48" height="48">
                        <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/>
                        <path d="M12 6v6l4 2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </div>
                <h1>Cookie Manager</h1>
                <p>QQ音乐Cookie管理系统</p>
            </div>
            <form id="loginForm" class="login-form">
                <div class="form-group">
                    <label for="token">访问令牌</label>
                    <input type="password" id="token" name="token" placeholder="请输入API Token" required>
                </div>
                <button type="submit" class="btn btn-primary btn-block">
                    <span>登录</span>
                    <svg viewBox="0 0 24 24" width="20" height="20">
                        <path d="M5 12h14M12 5l7 7-7 7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </button>
            </form>
            <div id="loginError" class="error-message" style="display: none;"></div>
        </div>
    </div>
    `;
    
    document.body.className = 'login-page';
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
}

async function handleLogin(e) {
    e.preventDefault();
    const token = document.getElementById('token').value;
    const errorEl = document.getElementById('loginError');
    
    try {
        authToken = token;
        localStorage.setItem('authToken', token);
        
        await apiRequest('/health');
        
        showDashboard();
        showToast('登录成功', 'success');
    } catch (error) {
        errorEl.textContent = 'Token无效，请重试';
        errorEl.style.display = 'block';
        authToken = null;
        localStorage.removeItem('authToken');
    }
}

function logout() {
    authToken = null;
    localStorage.removeItem('authToken');
    showLoginPage();
    showToast('已退出登录', 'info');
}

function showDashboard() {
    document.body.className = '';
    document.body.innerHTML = getDashboardHTML();
    initNavigation();
    loadDashboardData();
}

function getDashboardHTML() {
    return `
    <div class="app-container">
        <aside class="sidebar">
            <div class="sidebar-header">
                <div class="sidebar-brand">
                    <svg viewBox="0 0 24 24" width="32" height="32">
                        <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/>
                        <path d="M12 6v6l4 2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                    <span>Cookie Manager</span>
                </div>
            </div>
            <nav class="sidebar-nav">
                <div class="nav-section">
                    <div class="nav-section-title">主菜单</div>
                    <div class="nav-item active" data-page="dashboard">
                        <svg viewBox="0 0 24 24" width="20" height="20">
                            <rect x="3" y="3" width="7" height="7" rx="1" fill="none" stroke="currentColor" stroke-width="2"/>
                            <rect x="14" y="3" width="7" height="7" rx="1" fill="none" stroke="currentColor" stroke-width="2"/>
                            <rect x="3" y="14" width="7" height="7" rx="1" fill="none" stroke="currentColor" stroke-width="2"/>
                            <rect x="14" y="14" width="7" height="7" rx="1" fill="none" stroke="currentColor" stroke-width="2"/>
                        </svg>
                        <span>仪表盘</span>
                    </div>
                    <div class="nav-item" data-page="cookie">
                        <svg viewBox="0 0 24 24" width="20" height="20">
                            <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/>
                            <circle cx="8" cy="10" r="1" fill="currentColor"/>
                            <circle cx="16" cy="10" r="1" fill="currentColor"/>
                            <circle cx="10" cy="15" r="1" fill="currentColor"/>
                            <circle cx="15" cy="14" r="1" fill="currentColor"/>
                        </svg>
                        <span>Cookie管理</span>
                    </div>
                    <div class="nav-item" data-page="schedule">
                        <svg viewBox="0 0 24 24" width="20" height="20">
                            <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/>
                            <path d="M12 6v6l4 2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                        <span>定时任务</span>
                    </div>
                </div>
                <div class="nav-section">
                    <div class="nav-section-title">系统</div>
                    <div class="nav-item" data-page="settings">
                        <svg viewBox="0 0 24 24" width="20" height="20">
                            <circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="2"/>
                            <path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                        <span>系统设置</span>
                    </div>
                </div>
            </nav>
            <div class="sidebar-footer">
                <button class="btn btn-secondary btn-block" onclick="logout()">
                    <svg viewBox="0 0 24 24" width="18" height="18">
                        <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    <span>退出登录</span>
                </button>
            </div>
        </aside>
        <main class="main-content">
            <header class="header">
                <h1 class="header-title" id="pageTitle">仪表盘</h1>
                <div class="header-actions">
                    <button class="btn btn-primary" onclick="sendNow()">
                        <svg viewBox="0 0 24 24" width="18" height="18">
                            <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        <span>立即发送</span>
                    </button>
                    <button class="btn btn-secondary" onclick="refreshData()">
                        <svg viewBox="0 0 24 24" width="18" height="18">
                            <path d="M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        <span>刷新</span>
                    </button>
                </div>
            </header>
            <div class="content">
                <div id="pageContent"></div>
            </div>
        </main>
    </div>
    <div id="toastContainer" class="toast-container"></div>
    `;
}

function initNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', () => {
            document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            const page = item.dataset.page;
            showPage(page);
        });
    });
}

function showPage(page) {
    const content = document.getElementById('pageContent');
    const title = document.getElementById('pageTitle');
    
    switch(page) {
        case 'dashboard':
            title.textContent = '仪表盘';
            loadDashboardData();
            break;
        case 'cookie':
            title.textContent = 'Cookie管理';
            loadCookiePage();
            break;
        case 'schedule':
            title.textContent = '定时任务';
            loadSchedulePage();
            break;
        case 'settings':
            title.textContent = '系统设置';
            loadSettingsPage();
            break;
    }
}

async function loadDashboardData() {
    const content = document.getElementById('pageContent');
    content.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    
    try {
        const [status, metingCookie] = await Promise.all([
            apiRequest('/'),
            apiRequest('/api/meting').catch(() => null)
        ]);
        
        content.innerHTML = `
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-card-header">
                    <div class="stat-card-icon primary">
                        <svg viewBox="0 0 24 24" width="20" height="20">
                            <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/>
                            <circle cx="8" cy="10" r="1" fill="currentColor"/>
                            <circle cx="16" cy="10" r="1" fill="currentColor"/>
                        </svg>
                    </div>
                    <span class="badge ${metingCookie ? 'badge-success' : 'badge-danger'}">${metingCookie ? '有效' : '无效'}</span>
                </div>
                <div class="stat-card-value">${status.total_cookies}</div>
                <div class="stat-card-label">Cookie数量</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-header">
                    <div class="stat-card-icon success">
                        <svg viewBox="0 0 24 24" width="20" height="20">
                            <path d="M22 11.08V12a10 10 0 11-5.93-9.14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                            <path d="M22 4L12 14.01l-3-3" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </div>
                </div>
                <div class="stat-card-value">${status.total_hosts}</div>
                <div class="stat-card-label">主机数量</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-header">
                    <div class="stat-card-icon warning">
                        <svg viewBox="0 0 24 24" width="20" height="20">
                            <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/>
                            <path d="M12 6v6l4 2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                    </div>
                </div>
                <div class="stat-card-value">${metingCookie?.has_refresh_token ? '是' : '否'}</div>
                <div class="stat-card-label">支持续期</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-header">
                    <div class="stat-card-icon info">
                        <svg viewBox="0 0 24 24" width="20" height="20">
                            <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/>
                            <path d="M12 16v-4M12 8h.01" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                    </div>
                </div>
                <div class="stat-card-value">${status.status}</div>
                <div class="stat-card-label">服务状态</div>
            </div>
        </div>
        
        ${metingCookie ? `
        <div class="cookie-info-card">
            <div class="cookie-info-header">
                <h2 class="cookie-info-title">QQ音乐 Cookie 信息</h2>
                <div class="action-buttons">
                    <button class="btn btn-secondary btn-sm" onclick="copyCookie()">
                        <svg viewBox="0 0 24 24" width="16" height="16">
                            <rect x="9" y="9" width="13" height="13" rx="2" fill="none" stroke="currentColor" stroke-width="2"/>
                            <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" fill="none" stroke="currentColor" stroke-width="2"/>
                        </svg>
                        <span>复制</span>
                    </button>
                </div>
            </div>
            <div class="cookie-info-grid">
                <div class="cookie-info-item">
                    <div class="cookie-info-label">用户UIN</div>
                    <div class="cookie-info-value">${metingCookie.uin}</div>
                </div>
                <div class="cookie-info-item">
                    <div class="cookie-info-label">QQ Music Key</div>
                    <div class="cookie-info-value truncated">${metingCookie.qqmusic_key.substring(0, 30)}...</div>
                </div>
                <div class="cookie-info-item">
                    <div class="cookie-info-label">Refresh Token</div>
                    <div class="cookie-info-value">${metingCookie.has_refresh_token ? '已设置' : '未设置'}</div>
                </div>
                <div class="cookie-info-item">
                    <div class="cookie-info-label">更新时间</div>
                    <div class="cookie-info-value">${metingCookie.timestamp}</div>
                </div>
            </div>
        </div>
        ` : `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">暂无有效Cookie</h3>
            </div>
            <p style="color: var(--text-secondary);">请先通过代理抓取或手动添加Cookie</p>
        </div>
        `}
        `;
    } catch (error) {
        content.innerHTML = `<div class="error-message">加载失败: ${error.message}</div>`;
    }
}

async function loadCookiePage() {
    const content = document.getElementById('pageContent');
    content.innerHTML = `
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">Cookie操作</h3>
        </div>
        <div class="action-buttons">
            <button class="btn btn-primary" onclick="showAddCookieModal()">
                <svg viewBox="0 0 24 24" width="18" height="18">
                    <path d="M12 5v14M5 12h14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
                <span>添加Cookie</span>
            </button>
            <button class="btn btn-danger" onclick="clearAllCookies()">
                <svg viewBox="0 0 24 24" width="18" height="18">
                    <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span>清空所有</span>
            </button>
        </div>
    </div>
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">Meting-API 格式</h3>
        </div>
        <div id="metingCookieContent">
            <div class="loading"><div class="spinner"></div></div>
        </div>
    </div>
    `;
    
    try {
        const metingCookie = await apiRequest('/api/meting');
        document.getElementById('metingCookieContent').innerHTML = `
        <div class="code-block" id="cookieCode">${metingCookie.cookie}</div>
        <div style="margin-top: 12px;">
            <button class="btn btn-secondary btn-sm" onclick="copyToClipboard('${metingCookie.cookie}')">
                <svg viewBox="0 0 24 24" width="16" height="16">
                    <rect x="9" y="9" width="13" height="13" rx="2" fill="none" stroke="currentColor" stroke-width="2"/>
                    <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" fill="none" stroke="currentColor" stroke-width="2"/>
                </svg>
                <span>复制Cookie</span>
            </button>
        </div>
        `;
    } catch (error) {
        document.getElementById('metingCookieContent').innerHTML = `<div class="error-message">获取Cookie失败: ${error.message}</div>`;
    }
}

async function loadSchedulePage() {
    const content = document.getElementById('pageContent');
    content.innerHTML = `
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">定时任务配置</h3>
        </div>
        <div id="scheduleContent">
            <div class="loading"><div class="spinner"></div></div>
        </div>
    </div>
    `;
    
    try {
        const status = await apiRequest('/');
        document.getElementById('scheduleContent').innerHTML = `
        <div class="schedule-item">
            <div class="schedule-item-header">
                <span class="schedule-item-title">每日Cookie同步</span>
                <span class="badge badge-success">运行中</span>
            </div>
            <div class="schedule-item-info">
                <div>
                    <div class="schedule-info-label">执行时间</div>
                    <div class="schedule-info-value">每天 08:00</div>
                </div>
                <div>
                    <div class="schedule-info-label">目标API</div>
                    <div class="schedule-info-value">已配置</div>
                </div>
            </div>
        </div>
        <div class="action-buttons" style="margin-top: 16px;">
            <button class="btn btn-primary" onclick="sendNow()">
                <svg viewBox="0 0 24 24" width="18" height="18">
                    <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span>立即执行</span>
            </button>
        </div>
        `;
    } catch (error) {
        document.getElementById('scheduleContent').innerHTML = `<div class="error-message">加载失败: ${error.message}</div>`;
    }
}

function loadSettingsPage() {
    const content = document.getElementById('pageContent');
    content.innerHTML = `
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">系统设置</h3>
        </div>
        <div class="form-group">
            <label>API Token</label>
            <input type="password" value="${authToken}" readonly>
        </div>
        <div class="form-group">
            <label>API地址</label>
            <input type="text" value="${window.location.origin}" readonly>
        </div>
        <div class="form-group">
            <label>Meting-API端点</label>
            <input type="text" value="/api/meting" readonly>
        </div>
    </div>
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">快速操作</h3>
        </div>
        <div class="action-buttons">
            <button class="btn btn-secondary" onclick="copyApiUrl()">
                <svg viewBox="0 0 24 24" width="18" height="18">
                    <rect x="9" y="9" width="13" height="13" rx="2" fill="none" stroke="currentColor" stroke-width="2"/>
                    <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" fill="none" stroke="currentColor" stroke-width="2"/>
                </svg>
                <span>复制API地址</span>
            </button>
            <button class="btn btn-danger" onclick="logout()">
                <svg viewBox="0 0 24 24" width="18" height="18">
                    <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span>退出登录</span>
            </button>
        </div>
    </div>
    `;
}

async function sendNow() {
    try {
        showToast('正在发送Cookie...', 'info');
        const result = await schedulerManager.send_cookies_to_target();
        if (result.success) {
            showToast('Cookie发送成功', 'success');
        } else {
            showToast('发送失败: ' + result.error, 'error');
        }
    } catch (error) {
        showToast('发送失败: ' + error.message, 'error');
    }
}

function refreshData() {
    const activePage = document.querySelector('.nav-item.active');
    if (activePage) {
        showPage(activePage.dataset.page);
    }
    showToast('数据已刷新', 'success');
}

function copyCookie() {
    const code = document.getElementById('cookieCode');
    if (code) {
        copyToClipboard(code.textContent);
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('已复制到剪贴板', 'success');
    }).catch(() => {
        showToast('复制失败', 'error');
    });
}

function copyApiUrl() {
    copyToClipboard(window.location.origin + '/api/meting');
}

function showAddCookieModal() {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
    <div class="modal">
        <div class="modal-header">
            <h3 class="modal-title">添加Cookie</h3>
            <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">
                <svg viewBox="0 0 24 24" width="20" height="20">
                    <path d="M18 6L6 18M6 6l12 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
            </button>
        </div>
        <div class="modal-body">
            <div class="form-group">
                <label>UIN</label>
                <input type="text" id="inputUin" placeholder="QQ号">
            </div>
            <div class="form-group">
                <label>QQ Music Key</label>
                <input type="text" id="inputKey" placeholder="qqmusic_key">
            </div>
            <div class="form-group">
                <label>Refresh Token (可选)</label>
                <input type="text" id="inputRefreshToken" placeholder="psrf_qqrefresh_token">
            </div>
        </div>
        <div class="modal-footer">
            <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">取消</button>
            <button class="btn btn-primary" onclick="addCookie()">添加</button>
        </div>
    </div>
    `;
    document.body.appendChild(modal);
    setTimeout(() => modal.classList.add('active'), 10);
}

async function addCookie() {
    const uin = document.getElementById('inputUin').value;
    const key = document.getElementById('inputKey').value;
    const refreshToken = document.getElementById('inputRefreshToken').value;
    
    if (!uin || !key) {
        showToast('请填写UIN和Key', 'warning');
        return;
    }
    
    const cookies = {
        'qqmusic_uin': uin,
        'qqmusic_key': key
    };
    
    if (refreshToken) {
        cookies['psrf_qqrefresh_token'] = refreshToken;
    }
    
    try {
        await apiRequest('/api/cookies', {
            method: 'POST',
            body: JSON.stringify({
                source_host: 'y.qq.com',
                cookies: cookies
            })
        });
        
        document.querySelector('.modal-overlay').remove();
        showToast('Cookie添加成功', 'success');
        refreshData();
    } catch (error) {
        showToast('添加失败: ' + error.message, 'error');
    }
}

async function clearAllCookies() {
    if (!confirm('确定要清空所有Cookie吗？此操作不可恢复。')) {
        return;
    }
    
    try {
        await apiRequest('/api/cookies', { method: 'DELETE' });
        showToast('Cookie已清空', 'success');
        refreshData();
    } catch (error) {
        showToast('清空失败: ' + error.message, 'error');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (checkAuth()) {
        showDashboard();
    }
});
