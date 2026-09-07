from app.repositories.product import ProductRepository
from sqlalchemy.orm import Session
from app.schemas.product import ProductCreate, ProductResponse
from app.database.models import Product, ProductSize, ProductDough, ProductIngredient
from app.services.product.mapper import to_product_response
from uuid import UUID
from fastapi import HTTPException
from fastapi import status


class ProductService:

    def __init__(self, session: Session):
        self.repository = ProductRepository(session)

    def get_product_by_id(self, id: UUID) -> ProductResponse | None:
        product = self.repository.get_by_id(id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return to_product_response(product)

    def get_all_products(self) -> list[ProductResponse]:
        products = self.repository.get_all()
        return [to_product_response(product) for product in products]

    def create_product(self, data: ProductCreate) -> ProductResponse:
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
        created = self.repository.create(product)
        loaded = self.repository.get_by_id(created.id)
        if not loaded:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Product was created but could not be loaded",
            )
        return to_product_response(loaded)

    def delete(self, id: UUID) -> None:
        product = self.repository.get_by_id(id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        self.repository.delete(product)
