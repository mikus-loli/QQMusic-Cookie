import asyncio
import argparse
import threading
from typing import Optional
import uvicorn

from config import settings
from cookie_store import cookie_store
from proxy_capture import ProxyManager
from scheduler import scheduler_manager
from api_server import app


class QQMusicCookieManager:
    def __init__(self):
        self.proxy_manager: Optional[ProxyManager] = None
        self.api_thread: Optional[threading.Thread] = None
        self._running = False
    
    def _on_cookie_captured(self, capture_info: dict):
        host = capture_info.get("host", "unknown")
        cookies = capture_info.get("cookies", {})
        if cookies:
            cookie_store.save_cookies(host, cookies)
            print(f"[Manager] Auto-saved {len(cookies)} cookies from {host}")
    
    def _run_api_server(self):
        uvicorn.run(
            app,
            host=settings.API_HOST,
            port=settings.API_PORT,
            log_level="info"
        )
    
    async def start_full_service(self):
        print("=" * 50)
        print("QQ Music Cookie Manager - Full Service Mode")
        print("=" * 50)
        
        self._running = True
        
        self.api_thread = threading.Thread(
            target=self._run_api_server,
            daemon=True
        )
        self.api_thread.start()
        print(f"[Manager] API server started on http://{settings.API_HOST}:{settings.API_PORT}")
        
        scheduler_manager.setup_daily_schedule()
        scheduler_manager.start()
        print(f"[Manager] Scheduler started - daily task at {settings.SCHEDULE_HOUR:02d}:{settings.SCHEDULE_MINUTE:02d}")
        
        self.proxy_manager = ProxyManager(on_cookie_captured=self._on_cookie_captured)
        print(f"[Manager] Starting proxy on {settings.PROXY_HOST}:{settings.PROXY_PORT}")
        print("[Manager] Please configure QQ Music client to use this proxy")
        print("[Manager] Press Ctrl+C to stop")
        
        try:
            await self.proxy_manager.start_proxy()
        except KeyboardInterrupt:
            print("\n[Manager] Shutting down...")
            self.stop()
    
    def start_api_only(self):
        print("=" * 50)
        print("QQ Music Cookie Manager - API Only Mode")
        print("=" * 50)
        
        scheduler_manager.setup_daily_schedule()
        scheduler_manager.start()
        
        print(f"[Manager] API server starting on http://{settings.API_HOST}:{settings.API_PORT}")
        uvicorn.run(
            app,
            host=settings.API_HOST,
            port=settings.API_PORT,
            log_level="info"
        )
    
    def start_proxy_only(self):
        print("=" * 50)
        print("QQ Music Cookie Manager - Proxy Only Mode")
        print("=" * 50)
        
        self.proxy_manager = ProxyManager(on_cookie_captured=self._on_cookie_captured)
        print(f"[Manager] Starting proxy on {settings.PROXY_HOST}:{settings.PROXY_PORT}")
        print("[Manager] Please configure QQ Music client to use this proxy")
        
        self.proxy_manager.run_proxy_sync()
    
    def stop(self):
        self._running = False
        scheduler_manager.stop()
        print("[Manager] All services stopped")


def main():
    parser = argparse.ArgumentParser(
        description="QQ Music Cookie Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run full service (proxy + API + scheduler)
  python main.py --api-only         # Run API server only
  python main.py --proxy-only       # Run proxy capture only
  python main.py --send-now         # Send cookies immediately
  python main.py --status           # Show current status
        """
    )
    
    parser.add_argument(
        "--api-only",
        action="store_true",
        help="Run API server only (no proxy)"
    )
    parser.add_argument(
        "--proxy-only",
        action="store_true",
        help="Run proxy capture only (no API)"
    )
    parser.add_argument(
        "--send-now",
        action="store_true",
        help="Send cookies to target API immediately"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show current cookie status"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=settings.API_HOST,
        help=f"API server host (default: {settings.API_HOST})"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=settings.API_PORT,
        help=f"API server port (default: {settings.API_PORT})"
    )
    
    args = parser.parse_args()
    
    manager = QQMusicCookieManager()
    
    if args.status:
        all_cookies = cookie_store.get_all_cookies_flat()
        uin = all_cookies.get('qqmusic_uin') or all_cookies.get('uin', '')
        qqmusic_key = all_cookies.get('qqmusic_key', '')
        refresh_token = all_cookies.get('psrf_qqrefresh_token', '')
        
        print("\nQQ Music Cookie Status")
        print("=" * 40)
        
        if uin and qqmusic_key:
            print(f"  UIN: {uin}")
            print(f"  Key: {qqmusic_key[:20]}...")
            print(f"  Refresh Token: {'Yes' if refresh_token else 'No'}")
            print(f"  Status: Valid")
        else:
            print("  Status: No valid cookie found")
            print("  Please login QQ Music client first")
        return
    
    if args.send_now:
        async def send():
            result = await scheduler_manager.send_cookies_to_target()
            print(f"\nSend result: {result}")
        
        asyncio.run(send())
        return
    
    if args.api_only:
        manager.start_api_only()
        return
    
    if args.proxy_only:
        manager.start_proxy_only()
        return
    
    asyncio.run(manager.start_full_service())


if __name__ == "__main__":
    main()
