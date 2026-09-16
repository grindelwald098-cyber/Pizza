from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from app.schemas.cart import CartResponse
from app.schemas.guest import GuestResponse

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
    cart: CartResponse | None = None
    model_config = {
        "from_attributes": True
    }

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse | None = None
    guest: GuestResponse | None = None

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
