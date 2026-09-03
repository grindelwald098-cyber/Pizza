from app.repositories.sizes import SizesRepository
from app.schemas.sizes import SizeCreate, SizeResponse
from uuid import UUID
from sqlalchemy.orm import Session

class SizesService:
    def __init__(self, session: Session):
        self.repository = SizesRepository(session)  

    def get_all(self) -> list[SizeResponse]:
        return self.repository.get_all()

    def get_by_id(self, id: UUID) -> SizeResponse | None:
        return self.repository.get_by_id(id)

    def create(self, data: SizeCreate) -> SizeResponse:
        size = Size(
            id=data.id,
            name=data.name,
            diameter=data.diameter,
            sort_order=data.sort_order
        )   
        return self.repository.create(size)