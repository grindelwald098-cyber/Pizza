from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID

from app.database.models.dough_type import DoughType


class DoughTypeRepository: 

    def __init__ (self, session: Session):
        self.session = session

    def get_all(self) -> list[DoughType]:
        query = select(DoughType)
        return self.session.scalars(query).all()  

    def get_by_id(self, id: UUID) -> DoughType | None:
        query = select(DoughType).where(DoughType.id == id)
        return self.session.scalar(query)

    def get_existing_ids(self, ids: list[UUID]) -> set[UUID]:
        if not ids:
            return set()
        query = select(DoughType.id).where(DoughType.id.in_(ids))
        return set(self.session.scalars(query).all())

    def create(self, doughtype: DoughType) -> DoughType: 
        self.session.add(doughtype)    
        self.session.commit()
        self.session.refresh(doughtype)
        return doughtype        