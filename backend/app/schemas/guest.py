from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class GuestResponse(BaseModel):
    id: UUID
    cart_id: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class GuestTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    type: Literal["guest"] = "guest"
    guest: GuestResponse
