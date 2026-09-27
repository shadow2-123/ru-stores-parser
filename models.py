from enum import StrEnum
from pydantic import BaseModel, Field


class ShopId(StrEnum):
    dns = "dns"
    citilink = "citilink"


class ShopStatus(StrEnum):
    success = "success"
    empty = "empty"
    timeout = "timeout"
    blocked = "blocked"
    transport_down = "transport_down"
    error = "error"


class ShopResult(BaseModel):
    shop: ShopId
    status: ShopStatus
    query: str | None = None
    count: int = 0
    items: list[SearchItem] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    error: str | None = None

class SearchItem(BaseModel):
    product_id: str | None = None
    title: str | None = None
    url: str | None = None
    price: float | None = None

class SearchResponse(BaseModel):
    query: str
    results: list[ShopResult]

class ShopHealth(BaseModel):
    shop: ShopId
    status: ShopStatus
    detail: str | None = None


class HealthResponse(BaseModel):
    ok: bool
    chrome_cdp: bool
    shops: list[ShopHealth] = Field(default_factory=list)