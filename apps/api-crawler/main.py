import asyncio
from email import message
from faststream import FastStream
from faststream.redis import RedisBroker, ListSub
from faststream.exceptions import SkipMessage

from gw2_api import get_items
from shared import (
    UserSyncedPayload,
    InitUserRequest,
    InitUserResponse,
    DeleteUserRequest,
    DeleteUserResponse,
    Response,
    SuccessResponse,
    ErrorResponse,
    SyncUserRequest,
)
from config import config
from scripts.sync_users import sync_users
from service import get_user_ids, init_user, delete_user, sync_and_get_new_transactions

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils import async_batch_handler, generate_item_updates

broker = RedisBroker(config.redis_url)
app = FastStream(broker)

scheduler = AsyncIOScheduler()


@broker.subscriber("user_init")
async def handle_user_init(request: InitUserRequest) -> Response:
    try:
        user = await init_user(request.user_id, request.token)
        return SuccessResponse(payload=InitUserResponse(user_id=user.id))
    except Exception as exc:
        return ErrorResponse(message=str(exc))


@broker.subscriber("user_delete")
async def handle_user_delete(request: DeleteUserRequest) -> Response:
    try:
        await delete_user(request.user_id)
        return SuccessResponse(payload=DeleteUserResponse(user_id=request.user_id))
    except Exception as exc:
        return ErrorResponse(message=str(exc))


@broker.subscriber(list=ListSub("user_sync", batch=True))
@async_batch_handler
async def sync_user(request: SyncUserRequest):
    (bought, sold) = await sync_and_get_new_transactions(request.user_id)

    if len(bought) == 0 and len(sold) == 0:
        return

    print(f"{request.user_id} updated, syncing...")

    item_ids = list(set([transaction.item_id for transaction in bought + sold]))
    items = [] if len(item_ids) == 0 else await get_items(item_ids)

    updates_bought = generate_item_updates(bought, items)
    updates_sold = generate_item_updates(sold, items)

    payload = UserSyncedPayload(user_id=request.user_id, bought=updates_bought, sold=updates_sold)
    await broker.publish(payload, list="user_synced")


@scheduler.scheduled_job("interval", seconds=config.sync_interval)
async def sync_users_task():
    ids = await get_user_ids()
    requests = [SyncUserRequest(user_id=id) for id in ids]

    if len(ids) > 0:
        print("syncing users...")
        await broker.publish_batch(*requests, list="user_sync")


@app.on_startup
async def startup():
    scheduler.start()


@app.on_shutdown
async def shutdown():
    scheduler.shutdown()
