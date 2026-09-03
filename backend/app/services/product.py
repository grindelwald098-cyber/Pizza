from app.repositories.product import ProductRepository
from sqlalchemy.orm import Session
from app.schemas.product import ProductCreate
from app.database.models import Product
from uuid import UUID

class ProductService:

    def __init__(self, session: Session):
        self.repository  = ProductRepository(session)

    def get_product_by_id(self, id: UUID) -> Product | None:
        return self.repository.get_by_id(id)

    def get_all_products(self) -> list[Product]:
        return self.repository.get_all()

    def create_product(self, data: ProductCreate) -> Product: 
        product = Product(
            category_id=data.category_id,
            name=data.name,
            slug=data.slug,
            description=data.description,
            image_url=data.image_url,
            base_price=data.base_price,
            is_active=data.is_active,
            is_available=data.is_available,
        )
        return self.repository.create(product)

   