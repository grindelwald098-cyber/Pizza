from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.dough_type import DoughType


class DoughTypeRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[DoughType]:
        query = select(DoughType)

        result = await self.session.scalars(query)

        return list(result.all())

    async def get_by_id(self, id: UUID) -> DoughType | None:
        query = select(DoughType).where(DoughType.id == id)

        return await self.session.scalar(query)

    async def get_existing_ids(self, ids: list[UUID]) -> set[UUID]:
        if not ids:
            return set()

        query = select(DoughType.id).where(DoughType.id.in_(ids))

        result = await self.session.scalars(query)

        return set(result.all())

    async def create(self, dough_type: DoughType) -> DoughType:
        self.session.add(dough_type)

        await self.session.commit()
        await self.session.refresh(dough_type)

        return dough_type

    async def delete(self, dough_type: DoughType) -> None:
        try:
            await self.session.delete(dough_type)
            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise
