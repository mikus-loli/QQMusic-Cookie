import os
import sys
import time
import subprocess
import asyncio
import signal
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from cookie_store import cookie_store
from scheduler import scheduler_manager


class QQMusicController:
    QQ_MUSIC_PATHS = [
        r"C:\Program Files (x86)\Tencent\QQMusic\QQMusic.exe",
        r"C:\Program Files\Tencent\QQMusic\QQMusic.exe",
        r"D:\Program Files (x86)\Tencent\QQMusic\QQMusic.exe",
        r"D:\Program Files\Tencent\QQMusic\QQMusic.exe",
    ]
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.executable_path: Optional[str] = None
        self._find_executable()
    
    def _find_executable(self) -> bool:
        if settings.QQMUSIC_PATH and os.path.exists(settings.QQMUSIC_PATH):
            self.executable_path = settings.QQMUSIC_PATH
            print(f"[QQMusic] Found at: {settings.QQMUSIC_PATH}")
            return True
        
        for path in self.QQ_MUSIC_PATHS:
            if os.path.exists(path):
                self.executable_path = path
                print(f"[QQMusic] Found at: {path}")
                return True
        
        print("[QQMusic] QQ Music executable not found in default paths")
        print("[QQMusic] Please set QQMUSIC_PATH in .env file")
        return False
    
    def start(self) -> bool:
        if not self.executable_path:
            env_path = os.environ.get('QQMUSIC_PATH')
            if env_path and os.path.exists(env_path):
                self.executable_path = env_path
            else:
                print("[QQMusic] No valid executable path found")
                return False
        
        try:
            self.process = subprocess.Popen(
                [self.executable_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(f"[QQMusic] Started QQ Music (PID: {self.process.pid})")
            return True
        except Exception as e:
            print(f"[QQMusic] Failed to start: {e}")
            return False
    
    def stop(self) -> bool:
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=10)
                print("[QQMusic] QQ Music terminated gracefully")
                return True
            except subprocess.TimeoutExpired:
                self.process.kill()
                print("[QQMusic] QQ Music killed forcefully")
                return True
            except Exception as e:
                print(f"[QQMusic] Failed to stop: {e}")
                return False
        else:
            try:
                subprocess.run(
                    ["taskkill", "/F", "/IM", "QQMusic.exe"],
                    capture_output=True,
                    timeout=10
                )
                print("[QQMusic] QQ Music killed via taskkill")
                return True
            except Exception as e:
                print(f"[QQMusic] Failed to kill via taskkill: {e}")
                return False
    
    def is_running(self) -> bool:
        if self.process and self.process.poll() is None:
            return True
        
        try:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq QQMusic.exe"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return "QQMusic.exe" in result.stdout
        except:
            return False


class AutomationManager:
    def __init__(self):
        self.qqmusic = QQMusicController()
        self.proxy_process: Optional[subprocess.Popen] = None
        self.running = False
        self.cycle_count = 0
    
    def start_proxy(self) -> bool:
        print("[Proxy] Starting MITM proxy...")
        try:
            self.proxy_process = subprocess.Popen(
                [sys.executable, "main.py", "--proxy-only"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            time.sleep(3)
            if self.proxy_process.poll() is None:
                print(f"[Proxy] Proxy started (PID: {self.proxy_process.pid})")
                return True
            else:
                print("[Proxy] Failed to start proxy")
                return False
        except Exception as e:
            print(f"[Proxy] Error starting proxy: {e}")
            return False
    
    def stop_proxy(self) -> bool:
        if self.proxy_process:
            try:
                self.proxy_process.terminate()
                self.proxy_process.wait(timeout=10)
                print("[Proxy] Proxy stopped")
                return True
            except Exception as e:
                print(f"[Proxy] Error stopping proxy: {e}")
                self.proxy_process.kill()
                return True
        return True
    
    def clear_cookies(self) -> bool:
        try:
            cookie_file = settings.COOKIE_FILE
            if cookie_file.exists():
                cookie_file.unlink()
                print(f"[Cleanup] Deleted {cookie_file}")
            
            cookie_store.clear_all()
            print("[Cleanup] Cookie store cleared")
            return True
        except Exception as e:
            print(f"[Cleanup] Error clearing cookies: {e}")
            return False
    
    async def send_cookies(self) -> dict:
        print("[Send] Sending cookies to Meting-API...")
        result = await scheduler_manager.send_cookies_to_target()
        
        if result.get('success'):
            print(f"[Send] Successfully sent cookies")
            if result.get('data'):
                data = result['data']
                print(f"[Send] Cookie ID: {data.get('id', 'N/A')}")
        else:
            print(f"[Send] Failed: {result.get('error', 'Unknown error')}")
        
        return result
    
    def wait_for_cookies(self, timeout: int = 300) -> bool:
        print(f"[Wait] Waiting for cookies (timeout: {timeout}s)...")
        
        start_time = time.time()
        last_cookie_count = 0
        
        while time.time() - start_time < timeout:
            all_cookies = cookie_store.get_all_cookies_flat()
            cookie_count = len(all_cookies)
            
            qqmusic_uin = all_cookies.get('qqmusic_uin') or all_cookies.get('uin', '')
            qqmusic_key = all_cookies.get('qqmusic_key', '')
            
            if qqmusic_uin and qqmusic_key:
                print(f"[Wait] Valid cookies found!")
                print(f"[Wait] UIN: {qqmusic_uin}")
                print(f"[Wait] Key: {qqmusic_key[:20]}...")
                return True
            
            if cookie_count != last_cookie_count:
                print(f"[Wait] Captured {cookie_count} cookies...")
                last_cookie_count = cookie_count
            
            time.sleep(5)
        
        print("[Wait] Timeout - no valid cookies found")
        return False
    
    async def run_cycle(self) -> dict:
        print("\n" + "=" * 60)
        print(f"[Cycle] Starting cycle #{self.cycle_count + 1}")
        print(f"[Cycle] Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        result = {
            "cycle": self.cycle_count + 1,
            "success": False,
            "error": None
        }
        
        try:
            print("\n[Step 1/7] Starting proxy...")
            if not self.start_proxy():
                result["error"] = "Failed to start proxy"
                return result
            
            print("\n[Step 2/7] Waiting for proxy to stabilize (60s)...")
            for i in range(60, 0, -1):
                print(f"\r[Wait] {i} seconds remaining...", end="", flush=True)
                time.sleep(1)
            print("\r[Wait] Proxy ready!                    ")
            
            print("\n[Step 3/7] Starting QQ Music...")
            if not self.qqmusic.start():
                result["error"] = "Failed to start QQ Music"
                self.stop_proxy()
                return result
            
            print("\n[Step 4/7] Waiting for cookies...")
            time.sleep(10)
            
            if not self.wait_for_cookies(timeout=300):
                result["error"] = "No valid cookies captured"
            else:
                print("\n[Step 5/7] Sending cookies...")
                send_result = await self.send_cookies()
                result["success"] = send_result.get('success', False)
                result["send_result"] = send_result
            
            print("\n[Step 6/7] Stopping QQ Music...")
            self.qqmusic.stop()
            
            print("\n[Step 7/7] Stopping proxy and cleaning up...")
            self.stop_proxy()
            self.clear_cookies()
            
            self.cycle_count += 1
            result["cycle"] = self.cycle_count
            
        except Exception as e:
            result["error"] = str(e)
            print(f"[Error] {e}")
            self.qqmusic.stop()
            self.stop_proxy()
        
        print("\n" + "-" * 60)
        print(f"[Cycle] Cycle #{self.cycle_count} completed")
        print(f"[Cycle] Success: {result['success']}")
        if result.get('error'):
            print(f"[Cycle] Error: {result['error']}")
        print("-" * 60)
        
        return result
    
    async def run_forever(self, interval_hours: int = 24):
        print("\n" + "=" * 60)
        print("QQ Music Cookie Manager - Automation Mode")
        print("=" * 60)
        print(f"Interval: Every {interval_hours} hours")
        print(f"Proxy: {settings.PROXY_HOST}:{settings.PROXY_PORT}")
        print(f"Target API: {settings.TARGET_API_URL or 'Not configured'}")
        print("=" * 60 + "\n")
        
        if not settings.TARGET_API_URL or not settings.TARGET_API_TOKEN:
            print("[Error] TARGET_API_URL and TARGET_API_TOKEN must be configured!")
            return
        
        self.running = True
        
        while self.running:
            await self.run_cycle()
            
            if self.running:
                next_run = datetime.now() + timedelta(hours=interval_hours)
                print(f"\n[Sleep] Next run at: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"[Sleep] Waiting {interval_hours} hours...\n")
                
                for _ in range(interval_hours * 3600):
                    if not self.running:
                        break
                    await asyncio.sleep(1)
    
    def stop(self):
        print("\n[Stop] Stopping automation...")
        self.running = False
        self.qqmusic.stop()
        self.stop_proxy()


automation_manager = AutomationManager()


def signal_handler(sig, frame):
    print("\n[Signal] Received interrupt signal")
    automation_manager.stop()
    sys.exit(0)


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="QQ Music Cookie Automation")
    parser.add_argument("--interval", type=int, default=24, help="Interval in hours (default: 24)")
    parser.add_argument("--once", action="store_true", help="Run only once")
    args = parser.parse_args()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if args.once:
        await automation_manager.run_cycle()
    else:
        await automation_manager.run_forever(interval_hours=args.interval)


if __name__ == "__main__":
    asyncio.run(main())
