from app.database.models.cart_items import CartItem
from app.repositories.base import BaseRepository


class CartItemRepository(BaseRepository[CartItem]):
    model = CartItem
