import asyncio
from dns_connector.server import dns_search

async def main() -> None:
    result = await dns_search("ноутбук lenovo")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())