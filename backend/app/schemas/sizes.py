from pydantic import BaseModel
from uuid import UUID

class SizeCreate(BaseModel):
    name:str
    diameter:int
    sort_order:int

class SizeResponse(BaseModel):
    id:UUID
    name:str
    diameter:int
    sort_order:int
