from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID

from app.database.models.product import Product
from app.database.models.product_sizes import ProductSize


class ProductRepository:

    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[Product]:
        query = select(Product)
        return self.session.scalars(query).all()

    def get_by_id(self, id: UUID) -> Product | None:
        query = select(Product).where(Product.id == id)
        return self.session.scalar(query)

    def create(self, product: Product) -> Product:
        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        return product
        
    def create_product_with_sizes(self, data: Product,  sizes_ids: list[UUID], price_per_size: Decimal | None = None, is_available_per_size: bool | None = None) -> None:
        for size_id in sizes_ids:
            product_size = ProductSize(product_id=data.id, size_id=size_id, price=price_per_size, is_available=is_available_per_size)
            self.session.add(product_size)
        self.session.commit()


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

    def delete(self, id: UUID) -> None:
        product = self.get_by_id(id)
        if product:
            self.session.delete(product)
            self.session.commit()
            return True
        return False

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