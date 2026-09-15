from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_session
from app.database.models.ingredient import Ingredient
from app.schemas.ingredients import IngredientCreate, IngredientResponse
from app.services.ingredients import IngredientsService

router = APIRouter(
    prefix="/ingredients",
    tags=["Ingredients"],
)


@router.post("/", response_model=IngredientResponse)
async def create_ingredient(
    data: IngredientCreate, session: AsyncSession = Depends(get_session)
) -> Ingredient:
    service = IngredientsService(session)
    return await service.create(data)


@router.post("/list", response_model=list[IngredientResponse])
async def create_ingredients(
    data: list[IngredientCreate], session: AsyncSession = Depends(get_session)
) -> list[Ingredient]:
    service = IngredientsService(session)
    return await service.create_many(data)


@router.get("/", response_model=list[IngredientResponse])
async def get_ingredients(
    session: AsyncSession = Depends(get_session),
) -> list[Ingredient]:
    service = IngredientsService(session)
    return await service.get_all()


@router.get("/{id}", response_model=IngredientResponse)
async def get_ingredient_by_id(
    id: UUID, session: AsyncSession = Depends(get_session)
) -> Ingredient:
    service = IngredientsService(session)
    return await service.get_by_id(id)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ingredient(
    id: UUID, session: AsyncSession = Depends(get_session)
) -> None:
    service = IngredientsService(session)
    await service.delete(id)
