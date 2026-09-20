from datetime import datetime
from uuid import UUID

from app.schemas.product import CartItem
from pydantic import BaseModel


class CartResponse(BaseModel):
    id: UUID
    products: list[CartItem]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
