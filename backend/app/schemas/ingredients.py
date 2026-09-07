from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from pydantic import Field

class IngredientCreate(BaseModel):
    name: str
    description: str
    price: Decimal = Field(
        examples=[100.00]
    )
    image_url: str
    is_available: bool

class IngredientResponse(BaseModel):
    id: UUID
    name: str
    description: str
    price: Decimal = Field(
        examples=[100.00]
    )
    image_url: str
    is_available: bool