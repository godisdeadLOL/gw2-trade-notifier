from typing import Literal, Optional
from pydantic import TypeAdapter
from .schemas import Delivery, Item, TokenInfo, Transaction
from .client import get_client


async def get_delivery(access_token: str) -> Delivery:
    async with get_client(access_token=access_token) as client:
        response = await client.get("v2/commerce/delivery")
        body = response.text

    return Delivery.model_validate_json(body)


async def get_items(items: list[int]) -> list[Item]:
    params = {"ids": ",".join(map(str, items))}

    async with get_client() as client:
        response = await client.get("v2/items", params=params)
        body = response.text

    adapter = TypeAdapter(list[Item])
    return adapter.validate_json(body)


async def get_token_info(access_token: str) -> Optional[TokenInfo]:
    async with get_client(access_token) as client:
        response = await client.get("v2/tokeninfo")
        if response.status_code == 401:
            return None

        body = response.text

    return TokenInfo.model_validate_json(body)


async def get_transactions(
    mode: Literal["current", "history"], type: Literal["buys", "sells"], access_token: str
) -> list[Transaction]:
    async with get_client(access_token) as client:
        response = await client.get(f"v2/commerce/transactions/{mode}/{type}")
        body = response.text

    adapter = TypeAdapter(list[Transaction])
    return adapter.validate_json(body)
