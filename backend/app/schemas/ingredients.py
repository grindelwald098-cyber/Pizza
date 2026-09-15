from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from pydantic import Field

class IngredientCreate(BaseModel):
    name: str
    description: str | None = None
    price: Decimal = Field(
        examples=[100.00]
    )
    image_url: str | None = None
    is_available: bool = True
    

class IngredientResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    price: Decimal = Field(
        examples=[100.00]
    )
    image_url: str | None
    is_available: bool

    model_config = {
        "from_attributes": True
    }