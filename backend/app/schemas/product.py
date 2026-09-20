from decimal import Decimal
from uuid import UUID

from pydantic import Field
from pydantic import BaseModel
from app.schemas.category import CategoryResponse
from app.schemas.product_sizes import ProductSizeCreate, ProductSizeResponse
from app.schemas.product_ingredients import ProductIngredientCreate
from app.schemas.dough_type import DoughTypeResponse
from app.schemas.product_dough_types import ProductDoughTypeCreate
from app.schemas.product_ingredients import ProductIngredientResponse


class CartItem(BaseModel):
    product: ProductResponse
    quantity: int
    unit_price: Decimal = Field(
        examples=[100.00]
    )

    model_config = {
        "from_attributes": True
    }

class ProductCreate(BaseModel):
    category_id: UUID
    name: str
    slug: str
    description: str | None = None
    image_url: str | None = None
    base_price: Decimal = Field(
        examples=[100.00]
    )
    is_active: bool = True
    is_available: bool = True
    sizes: list[ProductSizeCreate] | None = None
    dough_types: list[ProductDoughTypeCreate] | None = None
    ingredients: list[ProductIngredientCreate] | None = None

class ProductResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: str | None
    image_url: str | None
    base_price: Decimal = Field(
        examples=[100.00]
    )
    is_active: bool
    is_available: bool
    category: CategoryResponse
    sizes: list[ProductSizeResponse]
    dough_types: list[DoughTypeResponse] | None = None
    ingredients: list[ProductIngredientResponse]
    model_config = {
        "from_attributes": True
    }

class ProductUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    image_url: str | None = None
    base_price: Decimal | None = None
    is_active: bool | None = None
    is_available: bool | None = None


class ProductUpdateDoughTypes(BaseModel):
    dough_types_ids: list[UUID]

class ProductUpdateIngredients(BaseModel):
    ingredients_ids: list[UUID]