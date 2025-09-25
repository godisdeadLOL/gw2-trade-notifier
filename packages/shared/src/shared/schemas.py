from typing import Any, Literal, Optional, Union
from pydantic import BaseModel, TypeAdapter


class SuccessResponse(BaseModel):
    type: Literal["success"] = "success"
    payload: Any


class ErrorResponse(BaseModel):
    type: Literal["error"] = "error"
    message: str


type Response = Union[SuccessResponse, ErrorResponse]
response_adapter: TypeAdapter[Response] = TypeAdapter(Response)


class ItemUpdate(BaseModel):
    name: str
    price: int
    count: int


# sync_user
class SyncUserRequest(BaseModel):
    user_id: str


class UserSyncedPayload(BaseModel):
    user_id: str
    bought: list[ItemUpdate]
    sold: list[ItemUpdate]


# init_user
class InitUserRequest(BaseModel):
    user_id: str
    token: str


class InitUserResponse(BaseModel):
    user_id: str


# delete_user
class DeleteUserRequest(BaseModel):
    user_id: str


class DeleteUserResponse(BaseModel):
    user_id: str
