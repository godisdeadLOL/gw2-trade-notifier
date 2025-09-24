from pydantic import BaseModel

class ItemUpdate(BaseModel):
    name: str
    price: int
    count: int


class UserSyncedPayload(BaseModel):
    user_id: str
    bought: list[ItemUpdate]
    sold: list[ItemUpdate]


class InitUserRequest(BaseModel):
    user_id: str
    token: str