from datetime import datetime
from uuid import UUID

from app.schemas.product import CartItem
from pydantic import BaseModel, Field


class CartResponse(BaseModel):
    id: UUID
    products: list[CartItem] = Field(default_factory=list, validation_alias="items")
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class AddProductToCartRequest(BaseModel):
    size_id: UUID | None = None
    dough_type_id: UUID | None = None
    extra_ingredient_ids: list[UUID] = []
    quantity: int = 1
