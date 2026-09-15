from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.dough_type import DoughType
from app.repositories.dough_type import DoughTypeRepository
from app.schemas.dough_type import DoughTypeCreate


class DoughTypeServices:

    def __init__(self, session: AsyncSession):
        self.repository = DoughTypeRepository(session)

    async def get_by_id(self, id: UUID) -> DoughType:
        dough_type = await self.repository.get_by_id(id)

        if not dough_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dough type not found",
            )

        return dough_type

    async def get_all(self) -> list[DoughType]:
        return await self.repository.get_all()

    async def create(self, data: DoughTypeCreate) -> DoughType:
        dough_type = DoughType(
            name=data.name,
            sort_order=data.sort_order,
            is_active=data.is_active,
        )

        return await self.repository.create(dough_type)

    async def delete(self, id: UUID) -> None:
        dough_type = await self.get_by_id(id)
        await self.repository.delete(dough_type)
