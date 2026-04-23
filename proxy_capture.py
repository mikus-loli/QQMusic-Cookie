import asyncio
import json
from datetime import datetime
from typing import Optional, Callable
from mitmproxy import http, ctx
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster
from config import settings


class QQMusicAddon:
    QQ_MUSIC_COOKIE_KEYS = [
        'qqmusic_uin',
        'qqmusic_key',
        'qqmusic_guid',
        'qqmusic_gkey',
        'qm_keyst',
        'psrf_qqrefresh_token',
        'psrf_qqaccess_token',
        'psrf_qqopenid',
        'uin',
        'skey',
        'p_skey',
    ]
    
    def __init__(self, on_cookie_captured: Optional[Callable] = None):
        self.on_cookie_captured = on_cookie_captured
        self.captured_cookies = {}
    
    def is_qq_music_request(self, host: str) -> bool:
        return any(domain in host for domain in settings.QQ_MUSIC_DOMAINS)
    
    def has_qq_music_cookies(self, cookie_header: str) -> bool:
        if not cookie_header:
            return False
        cookie_lower = cookie_header.lower()
        return any(key.lower() in cookie_lower for key in self.QQ_MUSIC_COOKIE_KEYS)
    
    def extract_cookies(self, cookie_header: str) -> dict:
        cookies = {}
        if cookie_header:
            for item in cookie_header.split(';'):
                item = item.strip()
                if '=' in item:
                    name, value = item.split('=', 1)
                    cookies[name.strip()] = value.strip()
        return cookies
    
    def request(self, flow: http.HTTPFlow) -> None:
        host = flow.request.host
        cookie_header = flow.request.headers.get("Cookie", "")
        
        is_qq_music_domain = self.is_qq_music_request(host)
        has_qq_cookies = self.has_qq_music_cookies(cookie_header)
        
        if cookie_header and (is_qq_music_domain or has_qq_cookies):
            cookies = self.extract_cookies(cookie_header)
            
            qq_music_cookies = {
                k: v for k, v in cookies.items()
                if any(key.lower() in k.lower() for key in self.QQ_MUSIC_COOKIE_KEYS)
            }
            
            if qq_music_cookies:
                self.captured_cookies.update(qq_music_cookies)
                
                capture_info = {
                    "host": host,
                    "url": flow.request.url,
                    "cookies": qq_music_cookies,
                    "timestamp": datetime.now().isoformat()
                }
                
                ctx.log.info(f"[QQ Music] Captured {len(qq_music_cookies)} cookies from {host}")
                
                if self.on_cookie_captured:
                    try:
                        self.on_cookie_captured(capture_info)
                    except Exception as e:
                        ctx.log.error(f"Callback error: {e}")


class ProxyManager:
    def __init__(self, on_cookie_captured: Optional[Callable] = None):
        self.addon = QQMusicAddon(on_cookie_captured)
        self.proxy_process = None
    
    def get_captured_cookies(self) -> dict:
        return self.addon.captured_cookies.copy()
    
    def clear_captured_cookies(self) -> None:
        self.addon.captured_cookies.clear()
    
    async def start_proxy(self) -> None:
        opts = Options(
            listen_host=settings.PROXY_HOST,
            listen_port=settings.PROXY_PORT,
            ssl_insecure=True,
        )
        
        m = DumpMaster(opts)
        m.addons.add(self.addon)
        
        print(f"[Proxy] Starting MITM proxy on {settings.PROXY_HOST}:{settings.PROXY_PORT}")
        print(f"[Proxy] SSL insecure mode enabled")
        print(f"[Proxy] Capturing all requests with QQ Music cookies")
        
        try:
            await m.run()
        except KeyboardInterrupt:
            print("[Proxy] Shutting down...")
            await m.done()
    
    def run_proxy_sync(self) -> None:
        asyncio.run(self.start_proxy())
