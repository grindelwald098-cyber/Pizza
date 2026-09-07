from pydantic import BaseModel
from uuid import UUID

class SizeCreate(BaseModel):
    name:str
    value:int
    unit:str
    sort_order:int

class SizeResponse(BaseModel):
    id:UUID
    name:str
    value:int
    unit:str
    sort_order:int
