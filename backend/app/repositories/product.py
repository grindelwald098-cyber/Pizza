from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from uuid import UUID

from app.database.models.product import Product
from app.database.models.product_sizes import ProductSize
from app.database.models.product_dough import ProductDough
from app.database.models.product_ingredients import ProductIngredient


class ProductRepository:

    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _load_options():
        return (
            selectinload(Product.category),
            selectinload(Product.sizes).selectinload(ProductSize.size),
            selectinload(Product.doughs).selectinload(ProductDough.dough_type),
            selectinload(Product.ingredients).selectinload(ProductIngredient.ingredient),
        )

    def get_all(self) -> list[Product]:
        query = select(Product).options(*self._load_options())
        return list(self.session.scalars(query).all())

    def get_by_id(self, id: UUID) -> Product | None:
        query = select(Product).where(Product.id == id).options(*self._load_options())
        return self.session.scalar(query)

    def create(self, product: Product) -> Product:
        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        return product

    def update(self, id: UUID, data: Product) -> Product:
        product = self.get_by_id(id)
        if product:
            product.category_id = data.category_id
            product.name = data.name
            product.slug = data.slug
            product.description = data.description or None
            product.image_url = data.image_url or None
            product.base_price = data.base_price
            product.is_active = data.is_active
            product.is_available = data.is_available
        self.session.commit()
        return product

    def delete(self, product: Product) -> None:
        try:
            self.session.delete(product)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    def add_sizes(self, id: UUID, sizes_ids: list[UUID]) -> None:
        product = self.get_by_id(id)
        if product:
            for size_id in sizes_ids:
                product_size = ProductSize(product_id=product.id, size_id=size_id)
                self.session.add(product_size)
            self.session.commit()
            return True
        return False

    def remove_sizes(self, id: UUID, sizes_ids: list[UUID]) -> None:
        product = self.get_by_id(id)
        if product:
            product.sizes_ids = [size_id for size_id in product.sizes_ids if size_id not in sizes_ids]
            self.session.commit()
            return True
        return False
