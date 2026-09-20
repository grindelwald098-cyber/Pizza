from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.carts import Cart
from app.repositories.cart import CartRepository
from app.repositories.cart_item import CartItemRepository
from app.repositories.product import ProductRepository
from app.utils.principals import GuestPrincipal, Principal, UserPrincipal


class CartService:
    def __init__(self, session: AsyncSession):
        self.cart_repository = CartRepository(session)
        self.product_repository = ProductRepository(session)
        self.cart_item_repository = CartItemRepository(session)

    async def get_cart_by_principal(self, principal: Principal) -> Cart | None:
        if isinstance(principal, UserPrincipal):
            return await self.cart_repository.get_by_user_id(principal.id)
        if isinstance(principal, GuestPrincipal):
            return await self.cart_repository.get_by_guest_id(principal.id)
        raise ValueError("Invalid principal type")

    async def create_cart(self) -> Cart:
        return await self.cart_repository.create(Cart())

    async def update_cart(self, cart: Cart) -> Cart:
        return await self.cart_repository.update(cart)

    async def add_product_to_cart(self, principal_id: UUID, product_id: UUID) -> Cart:

        cart = await self.get_cart_by_principal(principal_id)

        await self.cart_item_repository.add_product_to_cart(cart.id, product_id, quantity=1)

        return await self.cart_repository.add_product_to_cart(principal_id, product_id)