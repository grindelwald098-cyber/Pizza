from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel
from pydantic import Field


class ProductIngredientCreate(BaseModel):
    ingredient_id: UUID
    quantity: Decimal = Field(
        examples=[1.00]
    )
    is_default: bool = False
    is_active: bool = True


class ProductIngredientResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    price: Decimal = Field(
        examples=[100.00]
    )
    image_url: str | None
    is_available: bool
    quantity: Decimal = Field(
        examples=[1.00]
    )
    is_default: bool
    is_active: bool
    
    model_config = {
        "from_attributes": True
    }
