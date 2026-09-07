from app.database.models.sizes import Size
from sqlalchemy.orm import Session
from uuid import UUID
from sqlalchemy import select

class SizesRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[Size]:
        query = select(Size)
        return self.session.scalars(query).all()

    def get_by_id(self, id: UUID) -> Size | None:
        query = select(Size).where(Size.id == id)
        return self.session.scalar(query)

    def create(self, size: Size) -> Size:
        self.session.add(size)
        self.session.commit()
        self.session.refresh(size)
        return size

    def delete(self, size: Size) -> None:
        try:
            self.session.delete(size)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e