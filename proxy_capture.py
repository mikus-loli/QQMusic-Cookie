import asyncio
import json
from datetime import datetime
from typing import Optional, Callable
from mitmproxy import http, ctx
from mitmproxy.tools.main import mitmdump
from config import settings


class QQMusicAddon:
    def __init__(self, on_cookie_captured: Optional[Callable] = None):
        self.on_cookie_captured = on_cookie_captured
        self.captured_cookies = {}
    
    def is_qq_music_request(self, host: str) -> bool:
        return any(domain in host for domain in settings.QQ_MUSIC_DOMAINS)
    
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
        
        if self.is_qq_music_request(host):
            cookie_header = flow.request.headers.get("Cookie", "")
            
            if cookie_header:
                cookies = self.extract_cookies(cookie_header)
                
                if cookies:
                    self.captured_cookies.update(cookies)
                    
                    capture_info = {
                        "host": host,
                        "url": flow.request.url,
                        "cookies": cookies,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    ctx.log.info(f"[QQ Music] Captured cookies from {host}")
                    
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
        from mitmproxy.options import Options
        from mitmproxy.tools.dump import DumpMaster
        
        opts = Options(
            listen_host=settings.PROXY_HOST,
            listen_port=settings.PROXY_PORT,
        )
        
        m = DumpMaster(opts)
        m.addons.add(self.addon)
        
        print(f"[Proxy] Starting MITM proxy on {settings.PROXY_HOST}:{settings.PROXY_PORT}")
        print(f"[Proxy] Monitoring domains: {settings.QQ_MUSIC_DOMAINS}")
        
        try:
            await m.run()
        except KeyboardInterrupt:
            print("[Proxy] Shutting down...")
            await m.done()
    
    def run_proxy_sync(self) -> None:
        asyncio.run(self.start_proxy())
