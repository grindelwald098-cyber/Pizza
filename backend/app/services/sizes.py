from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.sizes import Size
from app.repositories.sizes import SizesRepository
from app.schemas.sizes import SizeCreate


class SizesService:

    def __init__(self, session: AsyncSession):
        self.repository = SizesRepository(session)

    async def get_all(self) -> list[Size]:
        sizes = await self.repository.get_all()
        sizes.sort(key=lambda x: x.sort_order)
        return sizes

    async def get_by_id(self, id: UUID) -> Size:
        size = await self.repository.get_by_id(id)

        if not size:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Size not found")

        return size

    async def create(self, data: SizeCreate) -> Size:
        size = Size(
            name=data.name,
            value=data.value,
            unit=data.unit,
            sort_order=data.sort_order,
        )

        return await self.repository.create(size)

    async def delete(self, id: UUID) -> None:
        size = await self.repository.get_by_id(id)

        if not size:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Size not found")

        await self.repository.delete(size)
