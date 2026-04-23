from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from datetime import datetime
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
