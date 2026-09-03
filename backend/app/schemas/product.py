from decimal import Decimal
from uuid import UUID

from app.schemas.category import CategoryResponse
from app.schemas.product_sizes import ProductSizeResponse
from pydantic import BaseModel


class ProductCreate(BaseModel):
    category_id: UUID
    name: str
    slug: str
    description: str | None = None
    image_url: str | None = None
    base_price: Decimal
    is_active: bool = True
    is_available: bool = True
    sizes_ids: list[UUID] | None = None
    dough_type_id: UUID | None = None
    ingredients_ids: list[UUID] | None = None
    price_per_size: Decimal | None = None
    is_available_per_size: bool | None = None

class ProductResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: str | None
    image_url: str | None
    base_price: Decimal
    is_active: bool
    is_available: bool

    sizes: list[ProductSizeResponse]

    category: CategoryResponse

    model_config = {
        "from_attributes": True
    }
