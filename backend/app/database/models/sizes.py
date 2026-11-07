from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.database.models.product_sizes import ProductSize


class Size(Base):
    __tablename__ = "sizes"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[int] = mapped_column(Integer, nullable=False)
    unit: Mapped[str] = mapped_column(String(10), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    
    product_sizes: Mapped[list["ProductSize"]] = relationship(
        "ProductSize",
        back_populates="size"
    )

