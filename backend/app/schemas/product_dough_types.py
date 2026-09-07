from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel
from app.schemas.dough_type import DoughTypeResponse
from pydantic import Field

class ProductDoughTypeCreate(BaseModel):
    dough_type_id: UUID
    is_default: bool

class ProductDoughTypeResponse(BaseModel):
    id: UUID
    dough_type: DoughTypeResponse
    is_default: bool

    model_config = {
        "from_attributes": True
    }