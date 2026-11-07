from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_session
from app.schemas.product import ProductCreate, ProductListResponse, ProductResponse, ProductUpdate
from app.schemas.product_dough_types import ProductDoughTypeCreate
from app.schemas.product_ingredients import ProductIngredientCreate
from app.schemas.product_sizes import ProductSizeCreate
from app.services.product import ProductService

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.post("/", response_model=ProductResponse)
async def create_product(
    data: ProductCreate, session: AsyncSession = Depends(get_session)
) -> ProductResponse:
    service = ProductService(session)
    return await service.create_product(data)


@router.get("/", response_model=ProductListResponse)
async def get_products(
    category_id: UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> ProductListResponse:
    service = ProductService(session)
    return await service.get_products(
        category_id=category_id,
        page=page,
        page_size=page_size,
    )


@router.get("/{id}", response_model=ProductResponse)
async def get_product_by_id(
    id: UUID, session: AsyncSession = Depends(get_session)
) -> ProductResponse:
    service = ProductService(session)
    return await service.get_product_by_id(id)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    id: UUID, session: AsyncSession = Depends(get_session)
) -> None:
    service = ProductService(session)
    await service.delete(id)


@router.patch("/{id}", response_model=ProductResponse)
async def update_product(
    id: UUID, data: ProductUpdate, session: AsyncSession = Depends(get_session)
) -> ProductResponse:
    service = ProductService(session)
    return await service.update_product(id, data)


@router.patch("/{id}/sizes", response_model=ProductResponse)
async def update_sizes_to_product(
    id: UUID,
    data: list[ProductSizeCreate],
    session: AsyncSession = Depends(get_session),
) -> ProductResponse:
    service = ProductService(session)
    return await service.update_sizes_to_product(id, data)


@router.patch("/{id}/dough_types", response_model=ProductResponse)
async def update_dough_types_to_product(
    id: UUID,
    data: list[ProductDoughTypeCreate],
    session: AsyncSession = Depends(get_session),
) -> ProductResponse:
    service = ProductService(session)
    return await service.update_dough_types_to_product(id, data)


@router.patch("/{id}/ingredients", response_model=ProductResponse)
async def update_ingredients_to_product(
    id: UUID,
    data: list[ProductIngredientCreate],
    session: AsyncSession = Depends(get_session),
) -> ProductResponse:
    service = ProductService(session)
    return await service.update_ingredients_to_product(id, data)
