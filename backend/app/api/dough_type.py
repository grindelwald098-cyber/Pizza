from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from app.schemas.dough_type import DoughTypeCreate, DoughTypeResponse
from app.database.models.dough_type import DoughType
from app.services.dough_type import DoughTypeServices
from app.database.database import get_session

router = APIRouter(
    prefix="/dough_types",
    tags=["Dough Types"],
)

@router.get("/", response_model=list[DoughTypeResponse])
def get_dough_types(session: Session = Depends(get_session)) -> list[DoughType]:
    service = DoughTypeServices(session)
    return service.get_all()

@router.get("/{id}", response_model=DoughTypeResponse)
def get_dough_type_by_id(id: UUID, session: Session = Depends(get_session)) -> DoughType:
    service = DoughTypeServices(session)
    return service.get_by_id(id)

@router.delete("/{id}", response_model=DoughTypeResponse)
def delete_dough_type(id: UUID, session: Session = Depends(get_session)) -> DoughType:
    service = DoughTypeServices(session)
    return service.delete(id)

@router.post("/", response_model=DoughTypeResponse)
def create_dough_type(data: DoughTypeCreate, session: Session = Depends(get_session)) -> DoughType:
    service = DoughTypeServices(session)
    return service.create(data)