import time

from playwright.async_api import async_playwright

from mcp_core.transport.chrome_cdp import NavBlocked, open_page

CDP = "http://127.0.0.1:9222"

CITILINK_OZON = (
    ("citilink", "https://www.citilink.ru/", ("citilink.ru", "www.citilink.ru"), 6000),
    ("ozon", "https://www.ozon.ru/", ("ozon.ru", "www.ozon.ru"), 6000),
)


def _still_challenge(html: str) -> bool:
    low = (html or "").lower()
    if "qrator" in low or "доступ ограничен" in low:
        return True
    return len(html or "") < 20000


async def warmup_dns() -> dict:
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP)
        page = await browser.contexts[0].new_page()
        try:
            await page.goto("https://www.dns-shop.ru/", wait_until="commit", timeout=30_000)
            deadline = time.monotonic() + 20
            html = ""
            while time.monotonic() < deadline:
                html = await page.content()
                if not _still_challenge(html):
                    return {"shop": "dns", "ok": True, "detail": "ready"}
                await page.wait_for_timeout(500)
            return {"shop": "dns", "ok": False, "detail": "still_challenge"}
        except Exception as exc:
            return {"shop": "dns", "ok": False, "detail": str(exc)[:200]}
        finally:
            # Вкладку DNS не закрываем — Qrator должен досчитаться.
            try:
                browser.disconnect()
            except Exception:
                pass


async def warmup_open_page(shop: str, url: str, hosts: tuple[str, ...], wait_ms: int) -> dict:
    try:
        async with open_page(url, wait_ms=wait_ms, allowed_hosts=hosts):
            return {"shop": shop, "ok": True, "detail": "ok"}
    except NavBlocked as exc:
        return {"shop": shop, "ok": False, "detail": f"blocked {exc.status}"}
    except Exception as exc:
        return {"shop": shop, "ok": False, "detail": str(exc)[:200]}


async def warmup_shops() -> dict:
    results = [await warmup_dns()]
    for shop, url, hosts, wait_ms in CITILINK_OZON:
        results.append(await warmup_open_page(shop, url, hosts, wait_ms))
    return {"ok": all(x["ok"] for x in results), "shops": results}