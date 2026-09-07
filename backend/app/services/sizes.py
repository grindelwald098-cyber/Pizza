from fastapi import HTTPException, status
from app.repositories.sizes import SizesRepository
from app.schemas.sizes import SizeCreate
from uuid import UUID
from sqlalchemy.orm import Session
from app.database.models.sizes import Size

class SizesService:
    def __init__(self, session: Session):
        self.repository = SizesRepository(session)  

    def get_all(self) -> list[Size]:
        sizes = self.repository.get_all()
        sizes.sort(key=lambda x: x.sort_order)
        return sizes 

    def get_by_id(self, id: UUID) -> Size:
        size = self.repository.get_by_id(id)
        if not size:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Size not found")
        return size

    def create(self, data: SizeCreate) -> Size:
        size = Size(
            name=data.name, 
            value=data.value,
            unit=data.unit,
            sort_order=data.sort_order
        )   
        return self.repository.create(size) 

    def delete(self, id: UUID) -> None:
        size = self.repository.get_by_id(id)
        if not size:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Size not found")
        self.repository.delete(size)
