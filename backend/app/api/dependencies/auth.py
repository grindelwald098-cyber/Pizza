from uuid import UUID

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_session
from app.database.models.users import User
from app.exceptions import ForbiddenError, UnauthorizedError
from app.repositories.permission import PermissionRepository
from app.repositories.user import UserRepository
from app.utils.jwt import decode_access_token
from app.utils.principals import GuestPrincipal, Principal, UserPrincipal

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    token = credentials.credentials

    try:
        payload = decode_access_token(token)
        user_id = UUID(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise UnauthorizedError.bearer() from None

    user = await UserRepository(session).get_by_id(user_id)

    if not user or not user.is_active:
        raise UnauthorizedError.bearer("User not found or inactive")

    return user


async def get_current_principal(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_session),
) -> Principal:

    try:
        payload = decode_access_token(credentials.credentials)
        principal_type = payload.get("type")
        principal_id = UUID(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError, TypeError):
        raise UnauthorizedError.bearer() from None

    if principal_type == "user":
        return UserPrincipal(id=principal_id)

    if principal_type == "guest":
        return GuestPrincipal(id=principal_id)

    raise UnauthorizedError.bearer()


def require_permission(permission: str):
    async def checker(
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
    ) -> User:
        permissions = await PermissionRepository(session).get_by_user_id(user.id)
        if permission not in permissions:
            raise ForbiddenError(
                "You do not have permission to access this resource",
            )
        return user
    return checker

optional_bearer = HTTPBearer(auto_error=False)

async def get_optional_guest_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(optional_bearer),
) -> UUID | None:
    if credentials is None:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        if payload.get("type") != "guest":
            return None
        return UUID(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError, TypeError):
        return None    