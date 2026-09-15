from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.permissions import Permission
from app.database.models.role_permissions import RolePermission
from app.database.models.user_roles import UserRole


class PermissionRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: UUID) -> Permission | None:
        query = select(Permission).where(Permission.id == id)

        return await self.session.scalar(query)

    async def get_by_name(self, name: str) -> Permission | None:
        query = select(Permission).where(Permission.name == name)

        return await self.session.scalar(query)

    async def get_all(self) -> list[Permission]:
        query = select(Permission)

        result = await self.session.scalars(query)

        return list(result.all())

    async def get_by_role_id(self, role_id: UUID) -> list[Permission]:
        query = (
            select(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(RolePermission.role_id == role_id)
        )

        result = await self.session.scalars(query)

        return list(result.all())

    async def get_by_user_id(self, user_id: UUID) -> list[Permission]:
        query = (
            select(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(UserRole, UserRole.role_id == RolePermission.role_id)
            .where(UserRole.user_id == user_id)
        )

        result = await self.session.scalars(query)

        return list(result.all())

    async def create(self, permission: Permission) -> Permission:
        self.session.add(permission)

        await self.session.commit()
        await self.session.refresh(permission)

        return permission

    async def update(self, permission: Permission) -> Permission:
        self.session.add(permission)

        await self.session.commit()
        await self.session.refresh(permission)

        return permission

    async def delete(self, permission: Permission) -> None:
        try:
            await self.session.delete(permission)
            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise

    async def assign_to_role(self, role_id: UUID, permission_id: UUID) -> RolePermission:
        role_permission = RolePermission(role_id=role_id, permission_id=permission_id)
        self.session.add(role_permission)

        await self.session.commit()
        await self.session.refresh(role_permission)

        return role_permission
