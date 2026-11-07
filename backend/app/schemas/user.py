from pydantic import BaseModel
from datetime import datetime
from typing import Literal
from uuid import UUID


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    first_name: str
    last_name: str
    phone: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    type: Literal["user"] = "user"
    user: UserResponse


class UserCreate(BaseModel):
    email: str
    first_name: str
    last_name: str
    password: str
    phone: str


class UserUpdate(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone: str


class UserUpdatePassword(BaseModel):
    password: str
    new_password: str
