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
        query = select(Product).where(Product.is_active.is_(True)).options(*self._load_options())
        return list(self.session.scalars(query).all())

    def get_by_id(self, id: UUID) -> Product | None:
        query = select(Product).where(Product.id == id, Product.is_active.is_(True)).options(*self._load_options())
        return self.session.scalar(query)

    def create(self, product: Product) -> Product:
        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        return product

    def update(self, product: Product) -> Product:
        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        return product

    def delete(self, product: Product) -> None:
        self.session.add(product)
        self.session.commit()