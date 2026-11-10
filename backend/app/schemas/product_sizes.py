from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel
from pydantic import Field

class ProductSizeCreate(BaseModel):
    size_id: UUID
    price: Decimal = Field(
        examples=[100.00]
    )
    is_available: bool
    is_default: bool = False
    image_url: str | None = None

class ProductSizeResponse(BaseModel):
    id:UUID
    name:str
    value:int
    unit:str
    sort_order:int
    price: Decimal = Field(
        examples=[100.00]
    )
    is_available: bool
    is_default: bool
    image_url: str | None = None

    model_config = {
        "from_attributes": True
    }