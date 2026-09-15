from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.roles import Role
from app.database.models.user_roles import UserRole


class RoleRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: UUID) -> Role | None:
        query = select(Role).where(Role.id == id)

        return await self.session.scalar(query)

    async def get_by_name(self, name: str) -> Role | None:
        query = select(Role).where(Role.name == name)

        return await self.session.scalar(query)

    async def get_all(self) -> list[Role]:
        query = select(Role)

        result = await self.session.scalars(query)

        return list(result.all())

    async def get_by_user_id(self, user_id: UUID) -> list[Role]:
        query = (
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
        )

        result = await self.session.scalars(query)

        return list(result.all())

    async def create(self, role: Role) -> Role:
        self.session.add(role)

        await self.session.commit()
        await self.session.refresh(role)

        return role

    async def update(self, role: Role) -> Role:
        self.session.add(role)

        await self.session.commit()
        await self.session.refresh(role)

        return role

    async def delete(self, role: Role) -> None:
        try:
            await self.session.delete(role)
            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise

    async def assign_to_user(self, user_id: UUID, role_id: UUID) -> UserRole:
        user_role = UserRole(user_id=user_id, role_id=role_id)
        self.session.add(user_role)

        await self.session.commit()
        await self.session.refresh(user_role)

        return user_role
