import asyncio

from shops.citilink import search_citilink
from shops.dns import search_dns


async def main() -> None:
    query = "ryzen 5 5600"
    dns_result, citilink_result = await asyncio.gather(
        search_dns(query),
        search_citilink(query),
    )
    print(dns_result)
    print(citilink_result)


if __name__ == "__main__":
    asyncio.run(main())