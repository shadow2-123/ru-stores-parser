import asyncio

import httpx
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from models import HealthResponse, SearchResponse, ShopHealth, ShopId, ShopStatus, ShopResult
from shops.citilink import search_citilink
from shops.dns import search_dns

app = FastAPI(title="ru-stores-parser")
_cdp_lock = asyncio.Lock()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def index():
    return FileResponse("static/index.html")


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    chrome_ok = False
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            r = await client.get("http://127.0.0.1:9222/json/version")
            chrome_ok = r.status_code == 200
    except httpx.HTTPError:
        pass
    return HealthResponse(
        ok=chrome_ok,
        chrome_cdp=chrome_ok,
        shops=[
            ShopHealth(
                shop=ShopId.dns,
                status=ShopStatus.success if chrome_ok else ShopStatus.transport_down,
            ),
            ShopHealth(
                shop=ShopId.citilink,
                status=ShopStatus.success if chrome_ok else ShopStatus.transport_down,
            ),
        ],
    )

@app.get("/search/dns", response_model=ShopResult)
async def search_dns_api(q: str = Query(min_length=1, max_length=200)) -> ShopResult:
    async with _cdp_lock:
        return await search_dns(q)


@app.get("/search/citilink", response_model=ShopResult)
async def search_citilink_api(q: str = Query(min_length=1, max_length=200)) -> ShopResult:
    async with _cdp_lock:
        return await search_citilink(q)

@app.get("/search", response_model=SearchResponse)
async def search(q: str = Query(min_length=1, max_length=200)) -> SearchResponse:
    async with _cdp_lock:
        dns_result, citilink_result = await asyncio.gather(
            search_dns(q),
            search_citilink(q),
        )
    return SearchResponse(query=q, results=[dns_result, citilink_result])