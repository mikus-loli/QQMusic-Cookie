import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Optional, Callable
from pathlib import Path
from mitmproxy import http, ctx
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster

sys.path.insert(0, str(Path(__file__).parent))
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
        self._master = None
    
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
        
        self._master = DumpMaster(opts)
        self._master.addons.add(self.addon)
        
        print(f"[Proxy] Starting MITM proxy on {settings.PROXY_HOST}:{settings.PROXY_PORT}")
        print(f"[Proxy] SSL insecure mode enabled")
        print(f"[Proxy] Capturing all requests with QQ Music cookies")
        
        try:
            await self._master.run()
        except KeyboardInterrupt:
            print("[Proxy] Shutting down...")
            await self.shutdown()
    
    async def shutdown(self) -> None:
        if self._master:
            try:
                await self._master.done()
            except Exception as e:
                print(f"[Proxy] Error during shutdown: {e}")
            self._master = None
    
    def run_proxy_sync(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.start_proxy())
        except KeyboardInterrupt:
            pass
        finally:
            try:
                loop.run_until_complete(self.shutdown())
            except:
                pass
            loop.close()


def run_standalone():
    print("[Proxy] Running in standalone mode...")
    print(f"[Proxy] Listening on {settings.PROXY_HOST}:{settings.PROXY_PORT}")
    
    manager = ProxyManager()
    
    def save_cookies_to_file(capture_info: dict):
        cookie_file = settings.COOKIE_FILE
        cookie_file.parent.mkdir(parents=True, exist_ok=True)
        
        existing = {}
        if cookie_file.exists():
            try:
                with open(cookie_file, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            except:
                existing = {}
        
        host = capture_info.get('host', 'unknown')
        cookies = capture_info.get('cookies', {})
        
        if host not in existing:
            existing[host] = {
                'cookies': {},
                'source_host': host,
                'captured_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
        
        existing[host]['cookies'].update(cookies)
        existing[host]['updated_at'] = datetime.now().isoformat()
        
        with open(cookie_file, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        
        print(f"[Store] Saved {len(cookies)} cookies from {host}")
    
    manager = ProxyManager(on_cookie_captured=save_cookies_to_file)
    manager.run_proxy_sync()


if __name__ == "__main__":
    run_standalone()
