import re

from mcp_core.errors import ParserDriftError, ToolError, TransportDownError
from ozon_connector.server import ozon_search

from models import SearchItem, ShopId, ShopResult, ShopStatus


def _price(raw) -> float | None:
    if raw is None or raw == "":
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    s = re.sub(r"[^\d]", "", str(raw))
    return float(s) if s else None


def shop_result_from_ozon(raw) -> ShopResult:
    items = [
        SearchItem(
            product_id=str(it.sku) if it.sku is not None else None,
            title=it.title,
            url=it.url,
            price=_price(it.price),
        )
        for it in raw.items
    ]
    warnings = list(getattr(raw.meta, "warnings", None) or [])
    return ShopResult(
        shop=ShopId.ozon,
        status=ShopStatus.success if items else ShopStatus.empty,
        query=raw.query,
        count=len(items),
        items=items,
        warnings=warnings,
    )


async def search_ozon(query: str) -> ShopResult:
    try:
        raw = await ozon_search(query)
        return shop_result_from_ozon(raw)
    except TransportDownError as exc:
        return ShopResult(shop=ShopId.ozon, status=ShopStatus.transport_down, query=query, error=str(exc))
    except (ParserDriftError, ToolError, Exception) as exc:
        return ShopResult(shop=ShopId.ozon, status=ShopStatus.error, query=query, error=str(exc))