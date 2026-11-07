from uuid import UUID

from sqlalchemy import select

from app.database.models.permissions import Permission
from app.database.models.role_permissions import RolePermission
from app.database.models.user_roles import UserRole
from app.repositories.base import BaseRepository


class PermissionRepository(BaseRepository[Permission]):
    model = Permission

    async def get_by_name(self, name: str) -> Permission | None:
        return await self.get_one_by(name=name)

    async def get_by_role_id(self, role_id: UUID) -> list[Permission]:
        statement = (
            select(Permission)
            .join(
                RolePermission,
                RolePermission.permission_id == Permission.id,
            )
            .where(RolePermission.role_id == role_id)
        )
        return await self._list(statement)

    async def get_by_user_id(self, user_id: UUID) -> list[Permission]:
        statement = (
            select(Permission)
            .join(
                RolePermission,
                RolePermission.permission_id == Permission.id,
            )
            .join(UserRole, UserRole.role_id == RolePermission.role_id)
            .where(UserRole.user_id == user_id)
        )
        return await self._list(statement)

    async def assign_to_role(
        self,
        role_id: UUID,
        permission_id: UUID,
    ) -> RolePermission:
        role_permission = RolePermission(
            role_id=role_id,
            permission_id=permission_id,
        )
        self.session.add(role_permission)
        await self.session.flush()
        return role_permission
