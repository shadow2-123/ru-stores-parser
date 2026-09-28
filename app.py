import asyncio

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from models import HealthResponse, SearchResponse, ShopHealth, ShopId, ShopStatus, ShopResult
from shops.citilink import search_citilink
from shops.dns import search_dns
from shops.ozon import search_ozon

import logging
import time
from pathlib import Path

Path("logs").mkdir(exist_ok=True)
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    encoding="utf-8",
)
log = logging.getLogger("parser")


app = FastAPI(title="ru-stores-parser")
_cdp_lock = asyncio.Lock()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def index():
    return FileResponse("static/index.html")

async def chrome_available() -> bool:
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection("127.0.0.1", 9222),
            timeout=2,
        )
        writer.write(b"GET /json/version HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n")
        await writer.drain()
        data = await asyncio.wait_for(reader.read(512), timeout=2)
        writer.close()
        return b"webSocketDebuggerUrl" in data or b"Browser" in data
    except Exception:
        return False

@app.get("/health/chrome")
async def health_chrome() -> dict:
    ok = await chrome_available()
    return {"ok": ok, "chrome_cdp": ok}

@app.get("/search/dns", response_model=ShopResult)
async def search_dns_api(q: str = Query(min_length=1, max_length=200)) -> ShopResult:
    t0 = time.perf_counter()
    async with _cdp_lock:
        result = await search_dns(q)
    log.info(
        "search shop=dns q=%r status=%s count=%s error=%r dt=%.1fs",
        q, result.status, result.count, result.error, time.perf_counter() - t0,
    )
    return result


@app.get("/search/citilink", response_model=ShopResult)
async def search_citilink_api(q: str = Query(min_length=1, max_length=200)) -> ShopResult:
    t0 = time.perf_counter()
    async with _cdp_lock:
        result = await search_citilink(q)
    log.info(
        "search shop=citilink q=%r status=%s count=%s error=%r dt=%.1fs",
        q, result.status, result.count, result.error, time.perf_counter() - t0,
    )
    return result


@app.get("/search/ozon", response_model=ShopResult)
async def search_ozon_api(q: str = Query(min_length=1, max_length=200)) -> ShopResult:
    return await search_ozon(q)