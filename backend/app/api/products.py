from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.database import get_session
from app.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    ProductUpdateIngredients,
)
from app.schemas.product_sizes import ProductSizeCreate
from app.schemas.product_dough_types import ProductDoughTypeCreate
from app.schemas.product_ingredients import ProductIngredientCreate

from app.services.product import ProductService 

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.post("/", response_model=ProductResponse)
def create_product(data: ProductCreate, session: Session = Depends(get_session)) -> ProductResponse:
    service = ProductService(session)
    return service.create_product(data)


@router.get("/", response_model=list[ProductResponse])
def get_products(session: Session = Depends(get_session)) -> list[ProductResponse]:
    service = ProductService(session)
    return service.get_all_products()


@router.get("/{id}", response_model=ProductResponse)
def get_product_by_id(id: UUID, session: Session = Depends(get_session)) -> ProductResponse:
    service = ProductService(session)
    return service.get_product_by_id(id)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(id: UUID, session: Session = Depends(get_session)) -> None:
    service = ProductService(session)
    service.delete(id)

@router.patch("/{id}", response_model=ProductResponse)
def update_product(id: UUID, data: ProductUpdate, session: Session = Depends(get_session)) -> ProductResponse:
    service = ProductService(session)
    return service.update_product(id, data)

@router.patch("/{id}/sizes", response_model=ProductResponse)
def update_sizes_to_product(id: UUID, data: list[ProductSizeCreate], session: Session = Depends(get_session)) -> ProductResponse:
    service = ProductService(session)
    return service.update_sizes_to_product(id, data)

@router.patch("/{id}/dough_types", response_model=ProductResponse)
def update_dough_types_to_product(id: UUID, data: list[ProductDoughTypeCreate] , session: Session = Depends(get_session)) -> ProductResponse:
    service = ProductService(session)
    return service.update_dough_types_to_product(id, data)

@router.patch("/{id}/ingredients", response_model=ProductResponse)
def update_ingredients_to_product(id: UUID, data: list[ProductIngredientCreate], session: Session = Depends(get_session)) -> ProductResponse:
    service = ProductService(session)
    return service.update_ingredients_to_product(id, data)