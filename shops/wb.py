from mcp_core.errors import ParserDriftError, ToolError, TransportDownError
from wb_connector.server import wb_search

from models import SearchItem, ShopId, ShopResult, ShopStatus


def shop_result_from_wb(raw, query: str) -> ShopResult:
    items = []
    for it in getattr(raw, "items", None) or []:
        nm = getattr(it, "nm_id", None)
        items.append(
            SearchItem(
                product_id=str(nm) if nm is not None else None,
                title=getattr(it, "name", None) or None,
                url=f"https://www.wildberries.ru/catalog/{nm}/detail.aspx" if nm else None,
                price=getattr(it, "price_rub", None),
            )
        )
    warnings = list(getattr(getattr(raw, "meta", None), "warnings", None) or [])
    return ShopResult(
        shop=ShopId.wb,
        status=ShopStatus.success if items else ShopStatus.empty,
        query=query,
        count=len(items),
        items=items,
        warnings=warnings,
    )


async def search_wb(query: str) -> ShopResult:
    try:
        raw = await wb_search(query)
        if getattr(raw, "status", None) == "no_results":
            return ShopResult(shop=ShopId.wb, status=ShopStatus.empty, query=query)
        return shop_result_from_wb(raw, query)
    except TransportDownError as exc:
        return ShopResult(shop=ShopId.wb, status=ShopStatus.transport_down, query=query, error=str(exc))
    except (ParserDriftError, ToolError, Exception) as exc:
        return ShopResult(shop=ShopId.wb, status=ShopStatus.error, query=query, error=str(exc))