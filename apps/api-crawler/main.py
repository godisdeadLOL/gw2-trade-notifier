import asyncio
from faststream import FastStream
from faststream.redis import RedisBroker, ListSub
from faststream.exceptions import SkipMessage

from gw2_api import get_items
from shared import InitUserRequest, UserSyncedPayload
from config import config
from scripts.sync_users import sync_users
from service import get_user_ids, init_user, delete_user, sync_and_get_new_transactions

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils import async_batch_handler, generate_item_updates

broker = RedisBroker(config.redis_url)
app = FastStream(broker)

scheduler = AsyncIOScheduler()


@broker.subscriber("user_init")
@broker.publisher("user_inited")
async def handle_user_init(payload: InitUserRequest) -> str:
    try:
        user = await init_user(payload.user_id, payload.token)
        return user.id
    except Exception as exc:
        await broker.publish((payload.user_id, str(exc)), "error")
        raise SkipMessage()


@broker.subscriber("user_delete")
@broker.publisher("user_deleted")
async def handle_user_delete(user_id: str):
    await delete_user(user_id)
    return user_id


@broker.subscriber(list=ListSub("user_sync", batch=True))
@async_batch_handler
async def sync_user(user_id: int):
    (bought, sold) = await sync_and_get_new_transactions(str(user_id))

    if len(bought) == 0 and len(sold) == 0:
        return
    
    print(f"{user_id} updated, syncing...")

    item_ids = list(set([transaction.item_id for transaction in bought + sold]))
    items = [] if len(item_ids) == 0 else await get_items(item_ids)

    updates_bought = generate_item_updates(bought, items)
    updates_sold = generate_item_updates(sold, items)

    payload = UserSyncedPayload(user_id=str(user_id), bought=updates_bought, sold=updates_sold)
    await broker.publish(payload, list="user_synced")
    

@scheduler.scheduled_job("interval", seconds=config.sync_interval)
async def sync_users_task():
    ids = await get_user_ids()
    if len(ids) > 0:
        print("syncing users")
        await broker.publish_batch(*ids, list="user_sync")


@app.on_startup
async def startup():
    scheduler.start()


@app.on_shutdown
async def shutdown():
    scheduler.shutdown()
