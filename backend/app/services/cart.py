from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.carts import Cart
from app.repositories.cart import CartRepository
from app.utils.principals import GuestPrincipal, Principal, UserPrincipal


class CartService:
    def __init__(self, session: AsyncSession):
        self.cart_repository = CartRepository(session)

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
