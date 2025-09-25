import asyncio
from typing import Any, Awaitable, Callable, TypeVar
from gw2_api import Transaction, Item
from shared import ItemUpdate


def generate_item_updates(transactions: list[Transaction], items: list[Item]):
    updates: dict[int, ItemUpdate] = {}

    for transaction in transactions:
        item = next(item for item in items if item.id == transaction.item_id)

        updates[item.id] = updates.get(item.id, None) or ItemUpdate(name=item.name, price=0, count=0)
        updates[item.id].price += transaction.price * transaction.quantity
        updates[item.id].count += transaction.quantity

    return list(updates.values())


T = TypeVar("T")


def async_batch_handler(func: Callable[[T], Awaitable]) -> Callable[[list[T]], Awaitable]:
    type = next(iter(func.__annotations__.values()))
    
    async def wrapper(values: list):
        await asyncio.gather(*[func(value) for value in values])

    wrapper.__annotations__["values"] = list[type]

    return wrapper

