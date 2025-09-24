from typing import Literal, Optional
from pydantic import BaseModel


class DeliveryItem(BaseModel):
    id: int
    count: int


class Delivery(BaseModel):
    coins: int
    items: list[DeliveryItem]


class Item(BaseModel):
    id: int
    name: str
    rarity: Literal["Junk", "Basic", "Fine", "Masterwork", "Rare", "Exotic", "Ascended", "Legendary"]


type Persmission = Literal[
    "account", "builds", "characters", "guilds", "inventories", "progression", "pvp", "tradingpost", "unlocks", "wallet"
]


class TokenInfo(BaseModel):
    name: str
    permissions: list[Persmission]


class Transaction(BaseModel):
    id: int
    item_id: int
    price: int
    quantity: int
    purchased: Optional[str] = None
