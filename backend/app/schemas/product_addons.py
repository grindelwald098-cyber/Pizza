from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class ProductAddonResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    image_url: str | None
    additional_price: Decimal = Field(examples=[100.00])
    is_available: bool

    model_config = {"from_attributes": True}
