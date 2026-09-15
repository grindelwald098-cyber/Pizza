from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_session
from app.database.models.sizes import Size
from app.schemas.sizes import SizeCreate, SizeResponse
from app.services.sizes import SizesService

router = APIRouter(
    prefix="/sizes",
    tags=["Sizes"],
)


@router.post("/", response_model=SizeResponse)
async def create_size(
    data: SizeCreate, session: AsyncSession = Depends(get_session)
) -> Size:
    service = SizesService(session)
    return await service.create(data)


@router.get("/", response_model=list[SizeResponse])
async def get_sizes(session: AsyncSession = Depends(get_session)) -> list[Size]:
    service = SizesService(session)
    return await service.get_all()


@router.get("/{id}", response_model=SizeResponse)
async def get_size_by_id(
    id: UUID, session: AsyncSession = Depends(get_session)
) -> Size:
    service = SizesService(session)
    return await service.get_by_id(id)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_size(id: UUID, session: AsyncSession = Depends(get_session)) -> None:
    service = SizesService(session)
    await service.delete(id)
