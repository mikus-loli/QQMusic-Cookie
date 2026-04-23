from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional
from datetime import datetime
from pathlib import Path
from cookie_store import cookie_store
from config import settings


security = HTTPBearer(auto_error=False)


app = FastAPI(
    title="QQMusic Cookie Manager API",
    description="Meting-API Cookie Provider",
    version="2.0.0",
    docs_url=None,
    redoc_url=None
)


static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not settings.API_TOKEN:
        return True
    if not credentials:
        raise HTTPException(status_code=401, detail="Authorization header required")
    if credentials.credentials != settings.API_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid API token")
    return True


@app.get("/")
async def root():
    return {
        "status": "running",
        "service": "qqmusic-cookie-manager",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/admin")
@app.get("/admin/{path:path}")
async def admin_panel(path: str = ""):
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"error": "Admin panel not found"}


@app.get("/api/meting", dependencies=[Depends(verify_token)])
async def get_meting_cookie():
    all_cookies = cookie_store.get_all_cookies_flat()
    
    uin = all_cookies.get('qqmusic_uin') or all_cookies.get('uin', '')
    qqmusic_key = all_cookies.get('qqmusic_key', '')
    refresh_token = all_cookies.get('psrf_qqrefresh_token', '')
    access_token = all_cookies.get('psrf_qqaccess_token', '')
    openid = all_cookies.get('psrf_qqopenid', '')
    qm_keyst = all_cookies.get('qm_keyst', '')
    guid = all_cookies.get('qqmusic_guid', '')
    
    if not uin or not qqmusic_key:
        raise HTTPException(status_code=404, detail="No valid QQ Music cookies found")
    
    cookie_parts = [f"uin={uin}", f"qqmusic_key={qqmusic_key}"]
    
    if refresh_token:
        cookie_parts.append(f"psrf_qqrefresh_token={refresh_token}")
    if access_token:
        cookie_parts.append(f"psrf_qqaccess_token={access_token}")
    if openid:
        cookie_parts.append(f"psrf_qqopenid={openid}")
    if qm_keyst:
        cookie_parts.append(f"qm_keyst={qm_keyst}")
    if guid:
        cookie_parts.append(f"qqmusic_guid={guid}")
    
    cookie_string = '; '.join(cookie_parts)
    
    return {
        "success": True,
        "platform": "tencent",
        "uin": uin,
        "qqmusic_key": qqmusic_key,
        "cookie": cookie_string,
        "refresh_token": refresh_token,
        "access_token": access_token,
        "openid": openid,
        "qm_keyst": qm_keyst,
        "guid": guid,
        "has_refresh_token": bool(refresh_token),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/meting/simple", dependencies=[Depends(verify_token)])
async def get_meting_cookie_simple():
    all_cookies = cookie_store.get_all_cookies_flat()
    
    uin = all_cookies.get('qqmusic_uin') or all_cookies.get('uin', '')
    qqmusic_key = all_cookies.get('qqmusic_key', '')
    
    if not uin or not qqmusic_key:
        raise HTTPException(status_code=404, detail="No valid QQ Music cookies found")
    
    return {
        "success": True,
        "cookie": f"uin={uin}; qqmusic_key={qqmusic_key}"
    }


from pydantic import BaseModel
from typing import Dict


class CookieCreateRequest(BaseModel):
    source_host: str
    cookies: Dict[str, str]


@app.post("/api/cookies", dependencies=[Depends(verify_token)])
async def create_cookies(request: CookieCreateRequest):
    cookie_store.save_cookies(request.source_host, request.cookies)
    return {
        "success": True,
        "message": f"Saved {len(request.cookies)} cookies for {request.source_host}"
    }


@app.delete("/api/cookies", dependencies=[Depends(verify_token)])
async def clear_all_cookies():
    cookie_store.clear_all()
    return {"success": True, "message": "All cookies cleared"}


@app.post("/api/send", dependencies=[Depends(verify_token)])
async def send_cookies_now():
    from scheduler import scheduler_manager
    result = await scheduler_manager.send_cookies_to_target()
    return result
