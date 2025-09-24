from pydantic import BaseModel

class User(BaseModel):
    id: str
    token: str
    transaction_ids: list[int]