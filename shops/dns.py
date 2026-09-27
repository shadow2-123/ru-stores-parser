from mcp_core.errors import ParserDriftError, ToolError, TransportDownError
from dns_connector.server import dns_search

from models import SearchItem, ShopId, ShopResult, ShopStatus


def shop_result_from_dns(raw) -> ShopResult:
    items = [
        SearchItem(
            product_id=it.product_id,
            title=it.title,
            url=it.url,
            price_rub=it.price_rub,
            old_price_rub=it.old_price_rub,
        )
        for it in raw.items
    ]
    warnings = list(getattr(raw.meta, "warnings", None) or [])
    status = ShopStatus.success if items else ShopStatus.empty
    return ShopResult(
        shop=ShopId.dns,
        status=status,
        query=raw.query,
        count=len(items),
        items=items,
        warnings=warnings,
    )


def shop_result_from_error(query: str, exc: BaseException) -> ShopResult:
    if isinstance(exc, TransportDownError):
        status = ShopStatus.transport_down
    elif isinstance(exc, ParserDriftError):
        status = ShopStatus.error
    else:
        status = ShopStatus.error
    return ShopResult(
        shop=ShopId.dns,
        status=status,
        query=query,
        error=str(exc),
    )


async def search_dns(query: str) -> ShopResult:
    try:
        raw = await dns_search(query)
        return shop_result_from_dns(raw)
    except (TransportDownError, ParserDriftError, ToolError, Exception) as exc:
        return shop_result_from_error(query, exc)