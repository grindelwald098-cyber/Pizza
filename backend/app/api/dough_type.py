from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_session
from app.database.models.dough_type import DoughType
from app.schemas.dough_type import DoughTypeCreate, DoughTypeResponse
from app.services.dough_type import DoughTypeService

router = APIRouter(
    prefix="/dough_types",
    tags=["Dough Types"],
)


@router.get("/", response_model=list[DoughTypeResponse])
async def get_dough_types(
    session: AsyncSession = Depends(get_session),
) -> list[DoughType]:
    service = DoughTypeService(session)
    return await service.get_all()


@router.get("/{id}", response_model=DoughTypeResponse)
async def get_dough_type_by_id(
    id: UUID, session: AsyncSession = Depends(get_session)
) -> DoughType:
    service = DoughTypeService(session)
    return await service.get_by_id(id)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dough_type(
    id: UUID, session: AsyncSession = Depends(get_session)
) -> None:
    service = DoughTypeService(session)
    await service.delete(id)


@router.post("/", response_model=DoughTypeResponse)
async def create_dough_type(
    data: DoughTypeCreate, session: AsyncSession = Depends(get_session)
) -> DoughType:
    service = DoughTypeService(session)
    return await service.create(data)
