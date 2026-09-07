from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from app.schemas.ingredients import IngredientCreate, IngredientResponse
from app.database.models.ingredient import Ingredient
from app.services.ingredients import IngredientsService
from app.database.database import get_session

router = APIRouter(
    prefix="/ingredients",
    tags=["Ingredients"],
)

@router.post("/", response_model=IngredientResponse)
def create_ingredient(data: IngredientCreate, session: Session = Depends(get_session)) -> Ingredient:
    service = IngredientsService(session)
    return service.create(data)

@router.post("/list", response_model=list[IngredientResponse])
def create_ingredients(data: list[IngredientCreate], session: Session = Depends(get_session)) -> list[Ingredient]:
    service = IngredientsService(session)
    return service.create_many(data)

@router.get("/", response_model=list[IngredientResponse])
def get_ingredients(session: Session = Depends(get_session)) -> list[Ingredient]:
    service = IngredientsService(session)
    return service.get_all()

@router.get("/{id}", response_model=IngredientResponse)
def get_ingredient_by_id(id: UUID, session: Session = Depends(get_session)) -> Ingredient:
    service = IngredientsService(session)
    return service.get_by_id(id)

@router.delete("/{id}", response_model=IngredientResponse)
def delete_ingredient(id: UUID, session: Session = Depends(get_session)) -> Ingredient:
    service = IngredientsService(session)
    return service.delete(id)