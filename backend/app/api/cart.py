from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.dependencies.auth import get_current_principal
from app.database.database import get_session
from app.schemas.cart import AddProductToCartRequest, CartResponse, DeleteProductFromCartRequest, UpdateCartItemRequest
from app.services.cart import CartService
from app.utils.principals import Principal

router = APIRouter(
    prefix="/cart",
    tags=["Cart"],
)


@router.get("/", response_model=CartResponse)
async def get_cart(
    principal: Principal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_session),
) -> CartResponse:
    service = CartService(session)
    return await service.get_cart_response(principal)


@router.post("/add-product/{product_id}", response_model=CartResponse)
async def add_product_to_cart(
    product_id: UUID,
    data: AddProductToCartRequest,
    principal: Principal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_session),
) -> CartResponse:
    service = CartService(session)
    return await service.add_product_to_cart(principal, product_id, data)


@router.delete("/delete-product/{cart_item_id}", response_model=CartResponse)
async def delete_product_from_cart(
    cart_item_id: UUID,
    principal: Principal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_session),
) -> CartResponse:
    service = CartService(session)
    return await service.delete_product_from_cart(principal, cart_item_id)

@router.patch("/items/{cart_item_id}", response_model=CartResponse)
async def update_cart_item(
    cart_item_id: UUID,
    data: UpdateCartItemRequest,
    principal: Principal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_session),
) -> CartResponse:
    service = CartService(session)
    return await service.update_cart_item(principal, cart_item_id, data)