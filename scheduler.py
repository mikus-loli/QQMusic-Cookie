import asyncio
import httpx
from datetime import datetime
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MISSED, JobEvent
from cookie_store import cookie_store
from config import settings


class SchedulerManager:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.last_execution: Optional[datetime] = None
        self.execution_count: int = 0
        self.error_count: int = 0
        self._setup_listeners()
    
    def _setup_listeners(self):
        self.scheduler.add_listener(self._on_job_error, EVENT_JOB_ERROR)
        self.scheduler.add_listener(self._on_job_missed, EVENT_JOB_MISSED)
    
    def _on_job_error(self, event: JobEvent):
        self.error_count += 1
        print(f"[Scheduler] Job error: {event.exception}")
    
    def _on_job_missed(self, event: JobEvent):
        print(f"[Scheduler] Job missed at {event.scheduled_run_time}")
    
    async def send_cookies_to_target(self) -> dict:
        if not settings.TARGET_API_URL:
            print("[Scheduler] No target API URL configured, skipping send")
            return {"success": False, "error": "No target API URL configured"}
        
        cookies = cookie_store.get_all_cookies_flat()
        
        if not cookies:
            print("[Scheduler] No cookies to send")
            return {"success": False, "error": "No cookies available"}
        
        payload = {
            "cookies": cookies,
            "cookie_string": cookie_store.get_cookie_string(),
            "timestamp": datetime.now().isoformat(),
            "source": "qqmusic-cookie-manager"
        }
        
        headers = {"Content-Type": "application/json"}
        if settings.TARGET_API_TOKEN:
            headers["Authorization"] = f"Bearer {settings.TARGET_API_TOKEN}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    settings.TARGET_API_URL,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                
                self.last_execution = datetime.now()
                self.execution_count += 1
                
                print(f"[Scheduler] Successfully sent {len(cookies)} cookies to {settings.TARGET_API_URL}")
                return {
                    "success": True,
                    "cookies_sent": len(cookies),
                    "response_status": response.status_code
                }
                
        except httpx.HTTPStatusError as e:
            self.error_count += 1
            print(f"[Scheduler] HTTP error: {e.response.status_code} - {e.response.text}")
            return {"success": False, "error": f"HTTP {e.response.status_code}: {e.response.text}"}
            
        except httpx.RequestError as e:
            self.error_count += 1
            print(f"[Scheduler] Request error: {str(e)}")
            return {"success": False, "error": str(e)}
            
        except Exception as e:
            self.error_count += 1
            print(f"[Scheduler] Unexpected error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def scheduled_send_task(self):
        print(f"[Scheduler] Running scheduled task at {datetime.now().isoformat()}")
        result = await self.send_cookies_to_target()
        print(f"[Scheduler] Task result: {result}")
        return result
    
    def setup_daily_schedule(self, hour: int = None, minute: int = None):
        hour = hour if hour is not None else settings.SCHEDULE_HOUR
        minute = minute if minute is not None else settings.SCHEDULE_MINUTE
        
        trigger = CronTrigger(hour=hour, minute=minute)
        
        self.scheduler.add_job(
            self.scheduled_send_task,
            trigger=trigger,
            id="daily_cookie_send",
            name="Daily Cookie Send Task",
            replace_existing=True,
            misfire_grace_time=3600
        )
        
        print(f"[Scheduler] Scheduled daily task at {hour:02d}:{minute:02d}")
    
    def add_custom_schedule(self, job_id: str, cron_expression: str, job_func):
        trigger = CronTrigger.from_crontab(cron_expression)
        self.scheduler.add_job(
            job_func,
            trigger=trigger,
            id=job_id,
            replace_existing=True,
            misfire_grace_time=3600
        )
    
    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()
            print("[Scheduler] Scheduler started")
    
    def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            print("[Scheduler] Scheduler stopped")
    
    def get_status(self) -> dict:
        jobs = self.scheduler.get_jobs()
        return {
            "running": self.scheduler.running,
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": str(job.next_run_time) if job.next_run_time else None
                }
                for job in jobs
            ],
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "execution_count": self.execution_count,
            "error_count": self.error_count
        }
    
    async def run_once(self):
        return await self.scheduled_send_task()


scheduler_manager = SchedulerManager()
