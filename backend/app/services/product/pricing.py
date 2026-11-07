from decimal import Decimal
from uuid import UUID

from app.database.models.product import Product
from app.exceptions import BadRequestError


def _default_size_id(product: Product) -> UUID | None:
    available = [
        item for item in product.sizes if item.is_available and item.size is not None
    ]
    if not available:
        return None

    chosen = next((item for item in available if item.is_default), None)
    if chosen is None:
        chosen = min(available, key=lambda item: (item.size.sort_order, str(item.size_id)))
    return chosen.size_id


def _default_dough_id(product: Product) -> UUID | None:
    available = [
        item
        for item in product.doughs
        if item.dough_type is not None and item.dough_type.is_active
    ]
    if not available:
        return None

    chosen = next((item for item in available if item.is_default), None)
    if chosen is None:
        chosen = min(
            available,
            key=lambda item: (item.dough_type.sort_order, str(item.dough_type_id)),
        )
    return chosen.dough_type_id


def resolve_configuration(
    product: Product,
    size_id: UUID | None,
    dough_type_id: UUID | None,
) -> tuple[UUID | None, UUID | None]:
    """Подставляет размер и тесто по связям товара, если клиент их не прислал."""
    if size_id is None:
        size_id = _default_size_id(product)
    if dough_type_id is None:
        dough_type_id = _default_dough_id(product)
    return size_id, dough_type_id


def ensure_configuration(
    product: Product,
    size_id: UUID | None,
    dough_type_id: UUID | None,
    extra_ids: list[UUID],
) -> None:
    available_sizes = {item.size_id for item in product.sizes if item.is_available}
    if product.sizes:
        if size_id not in available_sizes:
            raise BadRequestError(
                "No available size for this product"
                if size_id is None
                else "This size is not available for this product"
            )
    elif size_id is not None:
        raise BadRequestError("This size is not available for this product")

    available_doughs = {
        item.dough_type_id
        for item in product.doughs
        if item.dough_type is not None and item.dough_type.is_active
    }
    if product.doughs:
        if dough_type_id not in available_doughs:
            raise BadRequestError(
                "No available dough for this product"
                if dough_type_id is None
                else "This dough is not available for this product"
            )
    elif dough_type_id is not None:
        raise BadRequestError("This dough is not available for this product")

    allowed_extras = {
        addon.ingredient_id for addon in product.addons if addon.is_available
    }
    unknown = [extra_id for extra_id in extra_ids if extra_id not in allowed_extras]
    if unknown:
        raise BadRequestError(f"Extras not allowed: {unknown}")


def calculate_unit_price(
    product: Product,
    size_id: UUID | None,
    extra_ids: list[UUID],
) -> Decimal:
    if size_id is None:
        price = product.base_price
    else:
        product_size = next(item for item in product.sizes if item.size_id == size_id)
        price = product_size.price

    addon_by_id = {addon.ingredient_id: addon for addon in product.addons}
    for extra_id in extra_ids:
        price += addon_by_id[extra_id].additional_price

    return price
