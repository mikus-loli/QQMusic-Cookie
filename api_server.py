from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime
from cookie_store import cookie_store
from config import settings


app = FastAPI(
    title="QQMusic Cookie Manager API",
    description="API for managing QQ Music cookies captured from proxy",
    version="1.0.0"
)


class CookieCreateRequest(BaseModel):
    source_host: str
    cookies: Dict[str, str]


class CookieUpdateRequest(BaseModel):
    cookies: Dict[str, str]


class CookieResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict] = None


class StatusResponse(BaseModel):
    status: str
    timestamp: str
    total_hosts: int
    total_cookies: int


@app.get("/", response_model=StatusResponse)
async def root():
    all_cookies = cookie_store.get_cookies()
    total_cookies = sum(
        len(record.get('cookies', {})) 
        for record in all_cookies.values()
    )
    return StatusResponse(
        status="running",
        timestamp=datetime.now().isoformat(),
        total_hosts=len(all_cookies),
        total_cookies=total_cookies
    )


@app.get("/api/cookies", response_model=CookieResponse)
async def get_all_cookies():
    cookies = cookie_store.get_cookies()
    return CookieResponse(
        success=True,
        message=f"Found {len(cookies)} hosts with cookies",
        data=cookies
    )


@app.get("/api/cookies/{source_host}", response_model=CookieResponse)
async def get_cookies_by_host(source_host: str):
    cookies = cookie_store.get_cookies(source_host)
    if not cookies:
        raise HTTPException(status_code=404, detail=f"No cookies found for host: {source_host}")
    return CookieResponse(
        success=True,
        message=f"Found cookies for {source_host}",
        data=cookies
    )


@app.get("/api/cookies/string")
async def get_cookie_string(source_host: Optional[str] = Query(None, description="Filter by source host")):
    cookie_string = cookie_store.get_cookie_string(source_host)
    return {
        "success": True,
        "cookie_string": cookie_string,
        "source_host": source_host
    }


@app.post("/api/cookies", response_model=CookieResponse)
async def create_cookies(request: CookieCreateRequest):
    cookie_store.save_cookies(request.source_host, request.cookies)
    return CookieResponse(
        success=True,
        message=f"Saved {len(request.cookies)} cookies for {request.source_host}",
        data=cookie_store.get_cookies(request.source_host)
    )


@app.put("/api/cookies/{source_host}", response_model=CookieResponse)
async def update_cookies(source_host: str, request: CookieUpdateRequest):
    success = cookie_store.update_cookies(source_host, request.cookies)
    if not success:
        raise HTTPException(status_code=404, detail=f"No cookies found for host: {source_host}")
    return CookieResponse(
        success=True,
        message=f"Updated {len(request.cookies)} cookies for {source_host}",
        data=cookie_store.get_cookies(source_host)
    )


@app.delete("/api/cookies/{source_host}", response_model=CookieResponse)
async def delete_cookies(source_host: str):
    success = cookie_store.delete_cookies(source_host)
    if not success:
        raise HTTPException(status_code=404, detail=f"No cookies found for host: {source_host}")
    return CookieResponse(
        success=True,
        message=f"Deleted cookies for {source_host}",
        data=None
    )


@app.delete("/api/cookies", response_model=CookieResponse)
async def clear_all_cookies():
    cookie_store.clear_all()
    return CookieResponse(
        success=True,
        message="All cookies cleared",
        data=None
    )


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
