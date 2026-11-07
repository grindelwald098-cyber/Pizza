from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database.database import AssociationBase
import uuid


class UserRole(AssociationBase):
    __tablename__ = "user_roles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True
    )
