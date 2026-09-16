from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from app.schemas.cart import CartResponse

class GuestResponse(BaseModel):
    id: UUID
    cart: CartResponse | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
