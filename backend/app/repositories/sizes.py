from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.sizes import Size


class SizesRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Size]:
        query = select(Size)

        result = await self.session.scalars(query)

        return list(result.all())

    async def get_by_id(self, id: UUID) -> Size | None:
        query = select(Size).where(Size.id == id)

        return await self.session.scalar(query)

    async def get_existing_ids(self, ids: list[UUID]) -> set[UUID]:
        if not ids:
            return set()

        query = select(Size.id).where(Size.id.in_(ids))

        result = await self.session.scalars(query)

        return set(result.all())

    async def create(self, size: Size) -> Size:
        self.session.add(size)

        await self.session.commit()
        await self.session.refresh(size)

        return size

    async def delete(self, size: Size) -> None:
        try:
            await self.session.delete(size)
            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise