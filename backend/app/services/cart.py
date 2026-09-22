from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.cart_items import CartItem
from app.database.models.carts import Cart
from app.database.models.cart_item_added_ingredients import CartItemAddedIngredient
from app.repositories.cart import CartRepository
from app.repositories.cart_item import CartItemRepository
from app.repositories.product import ProductRepository
from app.schemas.cart import AddProductToCartRequest, CartResponse
from app.schemas.product import CartItem as CartItemSchema
from app.services.product.mapper import to_product_response
from app.services.product.pricing import calculate_unit_price
from app.utils.principals import GuestPrincipal, Principal, UserPrincipal
from app.repositories.ingredients import IngredientsRepository

def to_cart_response(cart: Cart) -> CartResponse:
    return CartResponse(
        id=cart.id,
        products=[
            CartItemSchema(
                product=to_product_response(
                    item.product,
                    item.size_id,
                    item.dough_type_id,
                    added_extras=list(item.added_ingredients),
                ),
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in cart.items
        ],
        created_at=cart.created_at,
        updated_at=cart.updated_at,
    )


class CartService:
    def __init__(self, session: AsyncSession):
        self.cart_repository = CartRepository(session)
        self.product_repository = ProductRepository(session)
        self.cart_item_repository = CartItemRepository(session)
        self.ingredient_repository = IngredientsRepository(session)

    async def get_cart_by_principal(self, principal: Principal) -> Cart:
        if isinstance(principal, UserPrincipal):
            cart = await self.cart_repository.get_by_user_id(principal.id)
        elif isinstance(principal, GuestPrincipal):
            cart = await self.cart_repository.get_by_guest_id(principal.id)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid principal type",
            )

        if cart is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
        return cart

    async def get_cart_response(self, principal: Principal) -> CartResponse:
        cart = await self.get_cart_by_principal(principal)
        return to_cart_response(cart)

    async def create_cart(self) -> Cart:
        return await self.cart_repository.create(Cart())

    async def update_cart(self, cart: Cart) -> Cart:
        return await self.cart_repository.update(cart)

    async def _build_added_ingredients(
        self,
        extra_ingredient_ids: list[UUID],
    ) -> list[CartItemAddedIngredient]:
        added: list[CartItemAddedIngredient] = []
        for ingredient_id in dict.fromkeys(extra_ingredient_ids):
            ingredient = await self.ingredient_repository.get_by_id(ingredient_id)
            if ingredient is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ingredient {ingredient_id} is not available for this product",
                )
            added.append(
                CartItemAddedIngredient(
                    ingredient_id=ingredient_id,
                    price=ingredient.price,
                )
            )
        return added

    async def add_product_to_cart(
        self,
        principal: Principal,
        product_id: UUID,
        data: AddProductToCartRequest,
    ) -> CartResponse:
        cart = await self.get_cart_by_principal(principal)
        cart_id = cart.id

        product = await self.product_repository.get_by_id(product_id)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        extra_ingredient_ids = list(dict.fromkeys(data.extra_ingredient_ids))
        added_ingredients = await self._build_added_ingredients(extra_ingredient_ids)
        unit_price = calculate_unit_price(
            product,
            data.size_id,
            [extra.price for extra in added_ingredients],
        )

        existing = await self.cart_item_repository.find_matching(
            cart_id,
            product_id,
            size_id=data.size_id,
            dough_type_id=data.dough_type_id,
            extra_ingredient_ids=extra_ingredient_ids,
        )

        if existing is not None:
            existing.quantity += data.quantity
            existing.unit_price = unit_price
            await self.cart_item_repository.update(existing)
        else:
            cart_item = CartItem(
                cart_id=cart_id,
                product_id=product_id,
                size_id=data.size_id,
                dough_type_id=data.dough_type_id,
                quantity=data.quantity,
                unit_price=unit_price,
                added_ingredients=added_ingredients,
            )
            await self.cart_item_repository.add(cart_item)

        reloaded = await self.cart_repository.get_by_id(cart_id)
        if reloaded is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
        return to_cart_response(reloaded)
