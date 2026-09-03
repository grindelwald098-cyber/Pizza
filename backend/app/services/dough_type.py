from app.repositories.dough_type import DoughTypeRepository
from app.database.models.dough_type import DoughType
from app.schemas.dough_type import DoughTypeCreate
from sqlalchemy.orm import Session
from uuid import UUID

class DoughTypeServices: 
    def __init__(self, session: Session):
        self.repository = DoughTypeRepository(session)

    def get_by_id(self, id:UUID) -> DoughType:
        return self.repository.get_by_id(id)

    def get_all(self) -> list[DoughType]:
        return self.repository.get_all()    

    def create(self, data: DoughTypeCreate) -> DoughType:
        dough_type=DoughType(
            name=data.name,
            sort_order=data.sort_order,
            is_active=data.is_active,
        )
        return self.repository.create(dough_type)


            