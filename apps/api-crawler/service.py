from datetime import datetime, timezone
from gw2_api.methods import get_token_info, get_transactions, Transaction
from schemas import User
from db import db


def _filter_transactions(transactions: list[Transaction]):
    now = datetime.now(timezone.utc)

    return [
        transaction
        for transaction in transactions
        if (now - datetime.fromisoformat(transaction.purchased or "")).total_seconds() / 3600 < 12
    ]


async def fetch_transactions(token: str):
    bought = await get_transactions("history", "buys", token)
    sold = await get_transactions("history", "sells", token)

    bought = _filter_transactions(bought)
    sold = _filter_transactions(sold)

    transaction_ids = [transaction.id for transaction in bought + sold]

    return (bought, sold, transaction_ids)


async def init_user(user_id: str, token: str):
    info = await get_token_info(token)
    if not info:
        raise Exception("wrong token")

    verified = "account" in info.permissions and "tradingpost" in info.permissions
    if not verified:
        raise Exception("wrong permissions")

    (_, _, transaction_ids) = await fetch_transactions(token)

    collection = db.get_collection("users")

    user = User(id=user_id, token=token, transaction_ids=transaction_ids)
    await collection.find_one_and_replace({"id": user_id}, user.model_dump(), upsert=True)

    return user


async def delete_user(user_id: str):
    collection = db.get_collection("users")
    await collection.delete_one({"id": user_id})


async def sync_and_get_new_transactions(user_id: str):
    collection = db.get_collection("users")

    user_raw = await collection.find_one({"id": user_id})
    if not user_raw:
        raise Exception("user not found")
    user = User.model_validate(user_raw)

    (bought, sold, transaction_ids) = await fetch_transactions(user.token)

    # Получить новые покупки
    delta_bought: list[Transaction] = []
    for transaction in bought:
        if transaction.id in user.transaction_ids:
            continue

        delta_bought.append(transaction)

    # Получить новые продажи
    delta_sold: list[Transaction] = []
    for transaction in sold:
        if transaction.id in user.transaction_ids:
            continue

        delta_sold.append(transaction)

    await collection.update_one({"id": user_id}, {"$set": {"transaction_ids": transaction_ids}})

    return (delta_bought, delta_sold)


async def get_user_ids() -> list[str]:
    collection = db.get_collection("users")
    ids = [entry["id"] async for entry in collection.find({}, {"id": True})]

    return ids
