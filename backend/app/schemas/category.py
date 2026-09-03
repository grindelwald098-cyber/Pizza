from pydantic import BaseModel
from uuid import UUID


class CategoryCreate(BaseModel):
    name: str
    slug: str
    description: str | None = None
    image_url: str | None = None
    is_active: bool = True


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: str | None
    image_url: str | None
    is_active: bool

    model_config = {
        "from_attributes": True
    }