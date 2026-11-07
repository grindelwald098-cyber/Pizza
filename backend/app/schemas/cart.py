from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class CartProductResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    image_url: str | None
    base_price: Decimal = Field(examples=[100.00])
    is_active: bool
    is_available: bool


class CartSizeResponse(BaseModel):
    id: UUID
    name: str
    value: int
    unit: str
    sort_order: int


class CartDoughResponse(BaseModel):
    id: UUID
    name: str
    sort_order: int
    is_active: bool


class CartExtraResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    image_url: str | None
    price: Decimal = Field(examples=[100.00])


class CartLineResponse(BaseModel):
    id: UUID
    product: CartProductResponse
    size: CartSizeResponse | None
    dough: CartDoughResponse | None
    extras: list[CartExtraResponse]
    quantity: int
    unit_price: Decimal = Field(examples=[100.00])
    total_price: Decimal = Field(examples=[200.00])

    model_config = {"from_attributes": True}


class CartResponse(BaseModel):
    id: UUID
    items: list[CartLineResponse] = Field(default_factory=list)
    total: Decimal = Field(examples=[200.00])
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductToCartRequest(BaseModel):
    size_id: UUID | None = None
    dough_type_id: UUID | None = None
    extra_ingredient_ids: list[UUID] = []
    quantity: int = 1

class AddProductToCartRequest(ProductToCartRequest):
    pass

class DeleteProductFromCartRequest(ProductToCartRequest):
    pass 

class UpdateCartItemRequest(ProductToCartRequest):
    pass