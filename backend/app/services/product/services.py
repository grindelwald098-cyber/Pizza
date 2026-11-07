from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Product
from app.exceptions import BadRequestError, InternalError, NotFoundError
from app.repositories.base import BaseRepository
from app.repositories.category import CategoryRepository
from app.repositories.dough_type import DoughTypeRepository
from app.repositories.ingredients import IngredientsRepository
from app.repositories.product import ProductRepository
from app.repositories.sizes import SizesRepository
from app.schemas.product import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from app.schemas.product_dough_types import ProductDoughTypeCreate
from app.schemas.product_ingredients import ProductIngredientCreate
from app.schemas.product_sizes import ProductSizeCreate
from app.services.product.links import (
    ProductLink,
    dough_link,
    ingredient_link,
    size_link,
    sync_rows,
)
from app.services.product.mapper import to_product_response


def _ensure_unique_ids(label: str, ids: list[UUID]) -> None:
    if len(ids) != len(set(ids)):
        raise BadRequestError(f"Duplicate {label}")


def _ensure_size_defaults(sizes: list[ProductSizeCreate]) -> None:
    if not sizes:
        return

    defaults = [item for item in sizes if item.is_default]
    if len(defaults) != 1 or not defaults[0].is_available:
        raise BadRequestError("Product must have exactly one available default size")


def _ensure_dough_defaults(doughs: list[ProductDoughTypeCreate]) -> None:
    if not doughs:
        return

    default_count = sum(1 for item in doughs if item.is_default)
    if default_count != 1:
        raise BadRequestError("Product must have exactly one default dough")


class ProductService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = ProductRepository(session)
        self.category_repo = CategoryRepository(session)
        self.sizes_repo = SizesRepository(session)
        self.dough_repo = DoughTypeRepository(session)
        self.ingredients_repo = IngredientsRepository(session)

    async def _get_product_or_404(self, product_id: UUID) -> Product:
        product = await self.repository.get_by_id(product_id)
        if product is None:
            raise NotFoundError("Product not found")
        return product

    async def _require_ids(
        self,
        repository: BaseRepository[Any],
        ids: list[UUID],
        *,
        label: str,
        unique_label: str,
    ) -> None:
        _ensure_unique_ids(unique_label, ids)
        existing = await repository.get_existing_ids(ids)
        missing = set(ids) - existing
        if missing:
            raise NotFoundError(f"{label} not found: {sorted(missing, key=str)}")

    async def _sync_link(
        self,
        rows: list[Any],
        incoming: list[Any],
        link: ProductLink[Any, Any],
        repository: BaseRepository[Any],
    ) -> None:
        await self._require_ids(
            repository,
            [link.item_id(item) for item in incoming],
            label=link.label,
            unique_label=link.unique_label,
        )
        await sync_rows(self.repository.session, rows, incoming, link)

    async def _save_loaded(self, product: Product) -> Product:
        await self.repository.update(product)
        # Сбрасываем уже загруженные связи, чтобы selectinload собрал ответ заново.
        self.repository.session.expire(product)
        loaded = await self.repository.get_by_id(product.id)
        if loaded is None:
            raise InternalError("Product was updated but could not be loaded")
        return loaded

    async def get_product_by_id(self, product_id: UUID) -> ProductResponse:
        product = await self._get_product_or_404(product_id)
        return to_product_response(product)

    async def get_products(
        self,
        *,
        category_id: UUID | None,
        page: int,
        page_size: int,
    ) -> ProductListResponse:
        if category_id is not None:
            category = await self.category_repo.get_by_id(category_id)
            if category is None:
                raise NotFoundError("Category not found")

        products, total = await self.repository.list_page(
            category_id=category_id,
            limit=page_size,
            offset=(page - 1) * page_size,
        )
        return ProductListResponse(
            items=[to_product_response(product) for product in products],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def create_product(self, data: ProductCreate) -> ProductResponse:
        sizes = data.sizes or []
        dough_types = data.dough_types or []
        ingredients = data.ingredients or []
        _ensure_size_defaults(sizes)
        _ensure_dough_defaults(dough_types)

        await self._require_ids(
            self.category_repo,
            [data.category_id],
            label="category",
            unique_label="category",
        )
        await self._require_ids(
            self.sizes_repo,
            [item.size_id for item in sizes],
            label=size_link.label,
            unique_label=size_link.unique_label,
        )
        await self._require_ids(
            self.dough_repo,
            [item.dough_type_id for item in dough_types],
            label=dough_link.label,
            unique_label=dough_link.unique_label,
        )
        await self._require_ids(
            self.ingredients_repo,
            [item.ingredient_id for item in ingredients],
            label=ingredient_link.label,
            unique_label=ingredient_link.unique_label,
        )

        product = Product(
            category_id=data.category_id,
            name=data.name,
            slug=data.slug,
            description=data.description,
            image_url=data.image_url,
            base_price=data.base_price,
            is_active=data.is_active,
            is_available=data.is_available,
            sizes=[size_link.build(item) for item in sizes],
            doughs=[dough_link.build(item) for item in dough_types],
            ingredients=[ingredient_link.build(item) for item in ingredients],
        )
        created = await self.repository.create(product)
        return to_product_response(created)

    async def delete(self, product_id: UUID) -> None:
        product = await self._get_product_or_404(product_id)
        await self.repository.deactivate(product)

    async def update_product(
        self,
        product_id: UUID,
        data: ProductUpdate,
    ) -> ProductResponse:
        product = await self._get_product_or_404(product_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(product, field, value)
        updated = await self.repository.update(product)
        return to_product_response(updated)

    async def update_sizes_to_product(
        self,
        product_id: UUID,
        data: list[ProductSizeCreate],
    ) -> ProductResponse:
        product = await self._get_product_or_404(product_id)
        _ensure_size_defaults(data)
        if not data:
            if product.sizes:
                raise BadRequestError(
                    "Product must have exactly one available default size"
                )
            return to_product_response(product)

        await self._sync_link(product.sizes, data, size_link, self.sizes_repo)
        return to_product_response(await self._save_loaded(product))

    async def update_dough_types_to_product(
        self,
        product_id: UUID,
        data: list[ProductDoughTypeCreate],
    ) -> ProductResponse:
        product = await self._get_product_or_404(product_id)
        _ensure_dough_defaults(data)
        await self._sync_link(product.doughs, data, dough_link, self.dough_repo)
        return to_product_response(await self._save_loaded(product))

    async def update_ingredients_to_product(
        self,
        product_id: UUID,
        data: list[ProductIngredientCreate],
    ) -> ProductResponse:
        product = await self._get_product_or_404(product_id)
        await self._sync_link(
            product.ingredients,
            data,
            ingredient_link,
            self.ingredients_repo,
        )
        return to_product_response(await self._save_loaded(product))
