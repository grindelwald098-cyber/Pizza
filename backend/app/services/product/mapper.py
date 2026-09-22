from decimal import Decimal
from uuid import UUID

from app.schemas.product import ProductResponse
from app.schemas.product_sizes import ProductSizeResponse
from app.schemas.category import CategoryResponse
from app.schemas.dough_type import DoughTypeResponse
from app.schemas.product_ingredients import ProductIngredientResponse
from app.database.models.product import Product
from app.database.models.product_sizes import ProductSize
from app.database.models.product_dough import ProductDough
from app.database.models.product_ingredients import ProductIngredient
from app.database.models.cart_item_added_ingredients import CartItemAddedIngredient


def to_product_size_response(product_size: ProductSize) -> ProductSizeResponse:
    return ProductSizeResponse(
        id=product_size.size.id,
        name=product_size.size.name,
        value=product_size.size.value,
        unit=product_size.size.unit,
        sort_order=product_size.size.sort_order,
        price=product_size.price,
        is_available=product_size.is_available,
    )


def to_product_dough_type_response(product_dough: ProductDough) -> DoughTypeResponse:
    return DoughTypeResponse(
        id=product_dough.dough_type.id,
        name=product_dough.dough_type.name,
        sort_order=product_dough.dough_type.sort_order,
        is_active=product_dough.dough_type.is_active,
        is_default=product_dough.is_default,
    )


def to_product_ingredient_response(
    product_ingredient: ProductIngredient,
) -> ProductIngredientResponse:
    return ProductIngredientResponse(
        id=product_ingredient.ingredient.id,
        name=product_ingredient.ingredient.name,
        description=product_ingredient.ingredient.description,
        price=product_ingredient.ingredient.price,
        image_url=product_ingredient.ingredient.image_url,
        is_available=product_ingredient.ingredient.is_available,
        quantity=product_ingredient.quantity,
        is_default=product_ingredient.is_default,
        is_active=product_ingredient.is_active,
    )


def to_cart_extra_response(
    extra: CartItemAddedIngredient,
) -> ProductIngredientResponse:
    # Доп из глобальной таблицы ingredients + цена-снимок из корзины.
    return ProductIngredientResponse(
        id=extra.ingredient.id,
        name=extra.ingredient.name,
        description=extra.ingredient.description,
        price=extra.price,
        image_url=extra.ingredient.image_url,
        is_available=extra.ingredient.is_available,
        quantity=Decimal("1"),
        is_default=False,
        is_active=True,
    )


def to_product_response(
    product: Product,
    size_id: UUID | None = None,
    dough_type_id: UUID | None = None,
    added_extras: list[CartItemAddedIngredient] | None = None,
) -> ProductResponse:
    # size/dough — фильтр конфигурации; extras НЕ из product.ingredients.
    sizes = product.sizes
    if size_id is not None:
        sizes = [item for item in product.sizes if item.size_id == size_id]

    doughs = product.doughs
    if dough_type_id is not None:
        doughs = [item for item in product.doughs if item.dough_type_id == dough_type_id]

    if added_extras is not None:
        ingredients = [to_cart_extra_response(extra) for extra in added_extras]
    else:
        ingredients = [
            to_product_ingredient_response(ingredient)
            for ingredient in product.ingredients
        ]

    return ProductResponse(
        id=product.id,
        name=product.name,
        slug=product.slug,
        description=product.description,
        image_url=product.image_url,
        base_price=product.base_price,
        is_active=product.is_active,
        is_available=product.is_available,
        category=CategoryResponse.model_validate(product.category),
        sizes=[to_product_size_response(size) for size in sizes],
        dough_types=[to_product_dough_type_response(dough) for dough in doughs] or None,
        ingredients=ingredients,
    )
