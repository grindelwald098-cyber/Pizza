from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.database import get_session
from app.schemas.product import ProductCreate, ProductResponse
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
