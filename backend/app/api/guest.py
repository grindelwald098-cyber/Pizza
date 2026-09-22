from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_session
from app.schemas.guest import GuestTokenResponse
from app.services.guest import GuestService

router = APIRouter(
    prefix="/guests",
    tags=["Guests"],
)


@router.post("/register", response_model=GuestTokenResponse)
async def register(
    session: AsyncSession = Depends(get_session),
) -> GuestTokenResponse:
    service = GuestService(session)
    return await service.register()
