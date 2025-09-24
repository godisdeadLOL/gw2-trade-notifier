import asyncio
from service import get_user_ids
from config import config

from faststream.redis import RedisBroker


async def sync_users():
    ids = await get_user_ids()

    async with RedisBroker(config.redis_url) as broker:
        for id in ids:
            await broker.publish(id, "user_sync")


if __name__ == "__main__":
    asyncio.run(sync_users())
