from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.cart_item_added_ingredients import (
    CartItemAddedIngredient,
)
from app.database.models.cart_items import CartItem
from app.database.models.carts import Cart
from app.database.models.dough_type import DoughType
from app.database.models.guests import Guest
from app.database.models.product import Product
from app.database.models.sizes import Size
from app.exceptions import BadRequestError, NotFoundError
from app.repositories.cart import CartRepository
from app.repositories.cart_item import CartItemRepository
from app.repositories.product import ProductRepository
from app.schemas.cart import (
    AddProductToCartRequest,
    CartDoughResponse,
    CartExtraResponse,
    CartLineResponse,
    CartProductResponse,
    CartResponse,
    CartSizeResponse,
    UpdateCartItemRequest,
)
from app.services.product.pricing import (
    calculate_unit_price,
    ensure_configuration,
    resolve_configuration,
)
from app.utils.principals import GuestPrincipal, Principal, UserPrincipal


@dataclass(frozen=True)
class _LineSelection:
    size_id: UUID | None
    dough_type_id: UUID | None
    extra_ids: list[UUID]
    unit_price: Decimal
    size: Size | None
    dough_type: DoughType | None


def to_cart_product_response(product: Product) -> CartProductResponse:
    return CartProductResponse(
        id=product.id,
        name=product.name,
        description=product.description,
        image_url=product.image_url,
        base_price=product.base_price,
        is_active=product.is_active,
        is_available=product.is_available,
    )


def to_cart_extra_response(extra: CartItemAddedIngredient) -> CartExtraResponse:
    return CartExtraResponse(
        id=extra.ingredient.id,
        name=extra.ingredient.name,
        description=extra.ingredient.description,
        image_url=extra.ingredient.image_url,
        price=extra.price,
    )


def to_cart_size_response(item: CartItem) -> CartSizeResponse | None:
    if item.size is None:
        return None

    image_url = None
    for product_size in item.product.sizes:
        if product_size.size_id == item.size_id:
            image_url = product_size.image_url
            break

    return CartSizeResponse(
        id=item.size.id,
        name=item.size.name,
        value=item.size.value,
        unit=item.size.unit,
        sort_order=item.size.sort_order,
        image_url=image_url,
    )


def to_cart_dough_response(item: CartItem) -> CartDoughResponse | None:
    if item.dough_type is None:
        return None
    return CartDoughResponse(
        id=item.dough_type.id,
        name=item.dough_type.name,
        sort_order=item.dough_type.sort_order,
        is_active=item.dough_type.is_active,
    )


def to_cart_line_response(item: CartItem) -> CartLineResponse:
    return CartLineResponse(
        id=item.id,
        product=to_cart_product_response(item.product),
        size=to_cart_size_response(item),
        dough=to_cart_dough_response(item),
        extras=[to_cart_extra_response(extra) for extra in item.added_ingredients],
        quantity=item.quantity,
        unit_price=item.unit_price,
        total_price=item.unit_price * item.quantity,
    )


def to_cart_response(cart: Cart) -> CartResponse:
    items = [to_cart_line_response(item) for item in cart.items]
    return CartResponse(
        id=cart.id,
        items=items,
        total=sum((item.total_price for item in items), Decimal("0")),
        created_at=cart.created_at,
        updated_at=cart.updated_at,
    )


def find_same_line(
    items: list[CartItem],
    product_id: UUID,
    size_id: UUID | None,
    dough_type_id: UUID | None,
    extra_ids: set[UUID],
    skip_id: UUID | None = None,
) -> CartItem | None:
    for item in items:
        if skip_id is not None and item.id == skip_id:
            continue
        if item.product_id != product_id:
            continue
        if item.size_id != size_id or item.dough_type_id != dough_type_id:
            continue
        current = {extra.ingredient_id for extra in item.added_ingredients}
        if current == extra_ids:
            return item
    return None


class CartService:
    def __init__(self, session: AsyncSession):
        self.cart_repository = CartRepository(session)
        self.product_repository = ProductRepository(session)
        self.cart_item_repository = CartItemRepository(session)

    async def get_cart_by_principal(self, principal: Principal) -> Cart:
        if isinstance(principal, UserPrincipal):
            cart = await self.cart_repository.get_by_user_id(principal.id)
        elif isinstance(principal, GuestPrincipal):
            cart = await self.cart_repository.get_by_guest_id(principal.id)
        else:
            raise BadRequestError("Invalid principal type")

        if cart is None:
            raise NotFoundError("Cart not found")
        return cart

    def _item_in_cart(self, cart: Cart, cart_item_id: UUID) -> CartItem:
        cart_item = next((item for item in cart.items if item.id == cart_item_id), None)
        if cart_item is None:
            raise NotFoundError("Cart item not found")
        return cart_item

    async def get_cart_response(self, principal: Principal) -> CartResponse:
        cart = await self.get_cart_by_principal(principal)
        return to_cart_response(cart)

    async def create_cart(self) -> Cart:
        return await self.cart_repository.create(Cart())

    async def update_cart(self, cart: Cart) -> Cart:
        return await self.cart_repository.update(cart)

    def _build_added_ingredients(
        self,
        extra_ids: list[UUID],
        product: Product,
    ) -> list[CartItemAddedIngredient]:
        addon_by_id = {addon.ingredient_id: addon for addon in product.addons}
        added: list[CartItemAddedIngredient] = []
        for extra_id in extra_ids:
            addon = addon_by_id[extra_id]
            extra = CartItemAddedIngredient(
                ingredient_id=extra_id,
                price=addon.additional_price,
            )
            extra.ingredient = addon.ingredient
            added.append(extra)
        return added

    def _selection(
        self,
        product: Product,
        size_id: UUID | None,
        dough_type_id: UUID | None,
        extra_ingredient_ids: list[UUID],
    ) -> _LineSelection:
        extra_ids = list(dict.fromkeys(extra_ingredient_ids))
        resolved_size_id, resolved_dough_id = resolve_configuration(
            product,
            size_id,
            dough_type_id,
        )
        ensure_configuration(
            product,
            resolved_size_id,
            resolved_dough_id,
            extra_ids,
        )
        product_size = next(
            (item for item in product.sizes if item.size_id == resolved_size_id),
            None,
        )
        product_dough = next(
            (
                item
                for item in product.doughs
                if item.dough_type_id == resolved_dough_id
            ),
            None,
        )
        return _LineSelection(
            size_id=resolved_size_id,
            dough_type_id=resolved_dough_id,
            extra_ids=extra_ids,
            unit_price=calculate_unit_price(product, resolved_size_id, extra_ids),
            size=product_size.size if product_size is not None else None,
            dough_type=(
                product_dough.dough_type if product_dough is not None else None
            ),
        )

    async def add_product_to_cart(
        self,
        principal: Principal,
        product_id: UUID,
        data: AddProductToCartRequest,
    ) -> CartResponse:
        cart = await self.get_cart_by_principal(principal)
        product = await self.product_repository.get_by_id_for_cart(product_id)
        if product is None:
            raise NotFoundError("Product not found")

        selection = self._selection(
            product,
            data.size_id,
            data.dough_type_id,
            data.extra_ingredient_ids,
        )
        existing = find_same_line(
            list(cart.items),
            product_id,
            selection.size_id,
            selection.dough_type_id,
            set(selection.extra_ids),
        )
        if existing is not None:
            existing.quantity += data.quantity
            existing.unit_price = selection.unit_price
            await self.cart_item_repository.update(existing)
            return to_cart_response(cart)

        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            size_id=selection.size_id,
            dough_type_id=selection.dough_type_id,
            quantity=data.quantity,
            unit_price=selection.unit_price,
            added_ingredients=self._build_added_ingredients(
                selection.extra_ids,
                product,
            ),
        )
        cart_item.product = product
        cart_item.size = selection.size
        cart_item.dough_type = selection.dough_type
        cart.items.append(cart_item)
        await self.cart_item_repository.update(cart_item)
        return to_cart_response(cart)

    async def delete_product_from_cart(
        self,
        principal: Principal,
        cart_item_id: UUID,
    ) -> CartResponse:
        cart = await self.get_cart_by_principal(principal)
        cart_item = self._item_in_cart(cart, cart_item_id)
        cart.items.remove(cart_item)
        await self.cart_item_repository.delete(cart_item)
        return to_cart_response(cart)

    async def update_cart_item(
        self,
        principal: Principal,
        cart_item_id: UUID,
        data: UpdateCartItemRequest,
    ) -> CartResponse:
        cart = await self.get_cart_by_principal(principal)
        cart_item = self._item_in_cart(cart, cart_item_id)

        # sizes / doughs / addons нужны для проверки и цены.
        # У строки корзины продукт загружен без этих связей — lazy-load в async падает.
        product = await self.product_repository.get_by_id_for_cart(cart_item.product_id)
        if product is None:
            raise NotFoundError("Product not found")

        selection = self._selection(
            product,
            data.size_id,
            data.dough_type_id,
            data.extra_ingredient_ids,
        )
        same = find_same_line(
            list(cart.items),
            cart_item.product_id,
            selection.size_id,
            selection.dough_type_id,
            set(selection.extra_ids),
            skip_id=cart_item.id,
        )
        if same is not None:
            same.quantity += data.quantity
            same.unit_price = selection.unit_price
            cart.items.remove(cart_item)
            await self.cart_item_repository.delete(cart_item)
            await self.cart_item_repository.update(same)
            return to_cart_response(cart)

        cart_item.quantity = data.quantity
        cart_item.size_id = selection.size_id
        cart_item.dough_type_id = selection.dough_type_id
        cart_item.size = selection.size
        cart_item.dough_type = selection.dough_type
        cart_item.added_ingredients = self._build_added_ingredients(
            selection.extra_ids,
            product,
        )
        cart_item.unit_price = selection.unit_price
        await self.cart_item_repository.update(cart_item)
        return to_cart_response(cart)
    

    async def merge_guest_cart(self, guest_id: UUID, user_id: UUID) -> None:
        guest_cart = await self.cart_repository.get_by_guest_id(guest_id)
        user_cart = await self.cart_repository.get_by_user_id(user_id)
        if guest_cart is None or user_cart is None or not guest_cart.items:
            return

        for item in list(guest_cart.items):
            same = find_same_line(
                list(user_cart.items),
                item.product_id,
                item.size_id,
                item.dough_type_id,
                {extra.ingredient_id for extra in item.added_ingredients},
            )
            if same is not None:
                same.quantity += item.quantity
                same.unit_price = item.unit_price
                await self.cart_item_repository.delete(item)
            else:
                guest_cart.items.remove(item)
                item.cart_id = user_cart.id
                user_cart.items.append(item)

        guest = await self.cart_repository.session.get(Guest, guest_id)
        if guest is not None:
            guest.cart_id = None
