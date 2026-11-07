from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database.models.guests import Guest
from app.repositories.base import BaseRepository
from app.repositories.cart import CartRepository


class GuestRepository(BaseRepository[Guest]):
    model = Guest

    async def get_by_id(self, entity_id: UUID) -> Guest | None:
        statement = (
            select(Guest)
            .where(Guest.id == entity_id)
            .options(
                selectinload(Guest.cart).options(
                    *CartRepository._load_options(),
                )
            )
        )
        return await self.session.scalar(statement)
