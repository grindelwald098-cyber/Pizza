from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.schemas.sizes import SizeCreate, SizeResponse
from app.database.models.sizes import Size
from app.services.sizes import SizesService
from app.database.database import get_session

router = APIRouter(
    prefix="/sizes",
    tags=["Sizes"],
)

@router.post("/", response_model=SizeResponse)
def create_size(data: SizeCreate, session: Session = Depends(get_session)) -> Size:
    service = SizesService(session)
    return service.create(data)

@router.get("/", response_model=list[SizeResponse])
def get_sizes(session: Session = Depends(get_session)) -> list[Size]:
    service = SizesService(session)
    return service.get_all()

@router.get("/{id}", response_model=SizeResponse)
def get_size_by_id(id: UUID, session: Session = Depends(get_session)) -> Size:
    service = SizesService(session)
    return service.get_by_id(id)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_size(id: UUID, session: Session = Depends(get_session)) -> None:
    service = SizesService(session)
    service.delete(id)