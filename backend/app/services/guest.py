from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.guest import GuestRepository
from app.database.models.guests import Guest
from app.database.models.carts import Cart
from app.schemas.guest import GuestResponse
from app.schemas.user import TokenResponse
from app.utils.principals import GuestPrincipal, Principal
from app.utils.jwt import create_access_token
from fastapi import HTTPException

class GuestService:
    def __init__(self, session: AsyncSession):
        self.repository = GuestRepository(session)

    async def register(self) -> TokenResponse:
        guest = Guest(
            cart=Cart(),
        )
        created_guest = await self.repository.create(guest)

        return TokenResponse(
            access_token=create_access_token(created_guest.id, "guest"),
            guest=GuestResponse.model_validate(created_guest, from_attributes=True),
        )

    async def get_guest_by_principal(self, principal: Principal) -> GuestResponse:
        if isinstance(principal, GuestPrincipal):
            guest = await self.repository.get_by_id(principal.id)
            if not guest:
                raise HTTPException(status_code=404, detail="Guest not found")
            return GuestResponse.model_validate(guest, from_attributes=True)
        raise HTTPException(status_code=400, detail="Invalid principal type")