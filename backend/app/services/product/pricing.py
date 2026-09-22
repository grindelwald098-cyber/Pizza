from uuid import UUID
from decimal import Decimal

from app.database.models.product import Product


def calculate_unit_price(
    product: Product,
    size_id: UUID | None,
    extra_prices: list[Decimal] | None = None,
) -> Decimal:
    """Цена 1 шт: цена размера (или base_price) + суммы цен допов."""
    unit_price = product.base_price

    if size_id is not None:
        product_size = next(
            (item for item in product.sizes if item.size_id == size_id and item.is_available),
            None,
        )
        if product_size is not None:
            unit_price = product_size.price

    for price in extra_prices or []:
        unit_price += price

    return unit_price
