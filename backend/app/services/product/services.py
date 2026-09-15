from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Product, ProductDough, ProductIngredient, ProductSize
from app.repositories.category import CategoryRepository
from app.repositories.dough_type import DoughTypeRepository
from app.repositories.ingredients import IngredientsRepository
from app.repositories.product import ProductRepository
from app.repositories.sizes import SizesRepository
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.schemas.product_dough_types import ProductDoughTypeCreate
from app.schemas.product_ingredients import ProductIngredientCreate
from app.schemas.product_sizes import ProductSizeCreate
from app.services.product.mapper import to_product_response


class ProductService:

    def __init__(self, session: AsyncSession):
        self.repository = ProductRepository(session)
        self.category_repo = CategoryRepository(session)
        self.sizes_repo = SizesRepository(session)
        self.dough_repo = DoughTypeRepository(session)
        self.ingredients_repo = IngredientsRepository(session)

    def _ensure_ids_exist(self, label: str, requested: list[UUID], existing: set[UUID]) -> None:
        missing = set(requested) - existing

        if missing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{label} not found: {sorted(missing, key=str)}",
            )

    async def _get_product_or_404(self, id: UUID) -> Product:
        product = await self.repository.get_by_id(id)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        return product

    async def get_product_by_id(self, id: UUID) -> ProductResponse:
        product = await self._get_product_or_404(id)

        return to_product_response(product)

    async def get_all_products(self) -> list[ProductResponse]:
        products = await self.repository.get_all()

        return [to_product_response(product) for product in products]

    async def create_product(self, data: ProductCreate) -> ProductResponse:
        size_ids = [s.size_id for s in (data.sizes or [])]
        dough_ids = [d.dough_type_id for d in (data.dough_types or [])]
        ingredient_ids = [i.ingredient_id for i in (data.ingredients or [])]

        self._ensure_ids_exist(
            "category",
            [data.category_id],
            await self.category_repo.get_existing_ids([data.category_id]),
        )
        self._ensure_ids_exist(
            "size",
            size_ids,
            await self.sizes_repo.get_existing_ids(size_ids),
        )
        self._ensure_ids_exist(
            "dough_type",
            dough_ids,
            await self.dough_repo.get_existing_ids(dough_ids),
        )
        self._ensure_ids_exist(
            "ingredient",
            ingredient_ids,
            await self.ingredients_repo.get_existing_ids(ingredient_ids),
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
            sizes=[
                ProductSize(
                    size_id=size.size_id,
                    price=size.price,
                    is_available=size.is_available,
                )
                for size in (data.sizes or [])
            ],
            doughs=[
                ProductDough(
                    dough_type_id=dough_type.dough_type_id,
                    is_default=dough_type.is_default,
                )
                for dough_type in (data.dough_types or [])
            ],
            ingredients=[
                ProductIngredient(
                    ingredient_id=ingredient.ingredient_id,
                    quantity=ingredient.quantity,
                    is_default=ingredient.is_default,
                )
                for ingredient in (data.ingredients or [])
            ],
        )
        created = await self.repository.create(product)
        loaded = await self.repository.get_by_id(created.id)

        if not loaded:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Product was created but could not be loaded",
            )

        return to_product_response(loaded)

    async def delete(self, id: UUID) -> None:
        product = await self._get_product_or_404(id)

        product.is_active = False
        await self.repository.delete(product)

    async def update_product(self, id: UUID, data: ProductUpdate) -> ProductResponse:
        product = await self._get_product_or_404(id)

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(product, field, value)

        updated = await self.repository.update(product)

        return to_product_response(updated)

    async def update_sizes_to_product(
        self, id: UUID, data: list[ProductSizeCreate]
    ) -> ProductResponse:
        product = await self._get_product_or_404(id)

        product_sizes = product.sizes
        current_ids = {item.size_id for item in product_sizes}
        new_ids = {item.size_id for item in data}
        missing_ids = current_ids - new_ids

        for product_size in product_sizes:
            if product_size.size_id in missing_ids:
                product_size.is_available = False

        for size in data:
            if size.size_id in current_ids:
                for product_size in product_sizes:
                    if product_size.size_id == size.size_id:
                        product_size.price = size.price
                        product_size.is_available = True
                        break
            else:
                product_sizes.append(
                    ProductSize(
                        product_id=id,
                        size_id=size.size_id,
                        price=size.price,
                        is_available=True,
                    )
                )

        updated = await self.repository.update(product)

        return to_product_response(updated)

    async def update_dough_types_to_product(
        self, id: UUID, data: list[ProductDoughTypeCreate]
    ) -> ProductResponse:
        product = await self._get_product_or_404(id)

        product_dough_types = product.doughs
        current_ids = {item.dough_type_id for item in product_dough_types}

        for dough in data:
            if dough.dough_type_id not in current_ids:
                product_dough_types.append(
                    ProductDough(
                        product_id=id,
                        dough_type_id=dough.dough_type_id,
                        is_default=dough.is_default or False,
                    )
                )

        updated = await self.repository.update(product)

        return to_product_response(updated)

    async def update_ingredients_to_product(
        self, id: UUID, data: list[ProductIngredientCreate]
    ) -> ProductResponse:
        product = await self._get_product_or_404(id)

        product_ingredients = product.ingredients
        current_ids = {item.ingredient_id for item in product_ingredients}
        new_ids = {item.ingredient_id for item in data}
        missing_ids = current_ids - new_ids

        for ingredient in product_ingredients:
            if ingredient.ingredient_id in missing_ids:
                ingredient.is_active = False

        for ingredient in data:
            if ingredient.ingredient_id in current_ids:
                for product_ingredient in product_ingredients:
                    if product_ingredient.ingredient_id == ingredient.ingredient_id:
                        product_ingredient.quantity = ingredient.quantity
                        product_ingredient.is_default = ingredient.is_default
                        product_ingredient.is_active = True
                        break
            else:
                product_ingredients.append(
                    ProductIngredient(
                        product_id=id,
                        ingredient_id=ingredient.ingredient_id,
                        quantity=ingredient.quantity,
                        is_default=ingredient.is_default,
                    )
                )

        updated = await self.repository.update(product)

        return to_product_response(updated)
