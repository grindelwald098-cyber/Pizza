from pydantic import BaseModel
from uuid import UUID

class DoughTypeCreate(BaseModel): 
    name: str
    sort_order: int 
    is_active: bool

class DoughTypeResponse(BaseModel): 
    id: UUID
    name: str
    sort_order:int 
    is_active: bool
    is_default: bool

    model_config = {
        "from_attributes": True
    }