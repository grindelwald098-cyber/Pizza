from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel
from app.schemas.sizes import SizeResponse

class ProductSizeResponse(BaseModel):
    id: UUID
    size: SizeResponse
    price: Decimal
    is_available: bool

    model_config = {
        "from_attributes": True
    }