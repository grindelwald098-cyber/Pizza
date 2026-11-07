from uuid import UUID

from sqlalchemy import select

from app.database.models.roles import Role
from app.database.models.user_roles import UserRole
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    model = Role

    async def get_by_name(self, name: str) -> Role | None:
        return await self.get_one_by(name=name)

    async def get_by_user_id(self, user_id: UUID) -> list[Role]:
        statement = (
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
        )
        return await self._list(statement)

    async def assign_to_user(self, user_id: UUID, role_id: UUID) -> UserRole:
        user_role = UserRole(user_id=user_id, role_id=role_id)
        self.session.add(user_role)
        await self.session.flush()
        return user_role
