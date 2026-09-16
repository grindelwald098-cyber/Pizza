from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_session
from app.schemas.user import TokenResponse
from app.services.guest import GuestService

router = APIRouter(
    prefix="/guests",
    tags=["Guests"],
)

@router.post("/register", response_model=TokenResponse)
async def register(
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    service = GuestService(session)
    return await service.register()

