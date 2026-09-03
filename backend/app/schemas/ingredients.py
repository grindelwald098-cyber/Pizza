from pydantic import BaseModel
from uuid import UUID


class IngredientCreate(BaseModel):
    name: str
    description: str
    price: float
    quantity: int
    unit: str
    image_url: str
    category: str
    sub_category: str
    brand: str
    origin: str
    is_organic: bool
    is_gluten_free: bool
    is_vegan: bool

class IngredientResponse(BaseModel):
    id: UUID
    name: str
    description: str
    price: float
    quantity: int
    unit: str
    image_url: str
    category: str
    sub_category: str
    brand: str
    origin: str
    is_organic: bool
    is_gluten_free: bool
    is_vegan: bool