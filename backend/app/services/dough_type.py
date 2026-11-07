from app.database.models.dough_type import DoughType
from app.repositories.dough_type import DoughTypeRepository
from app.schemas.dough_type import DoughTypeCreate
from app.services.crud import CrudService


class DoughTypeService(CrudService[DoughType, DoughTypeCreate]):
    repository_cls = DoughTypeRepository
    not_found_detail = "Dough type not found"

    def build(self, data: DoughTypeCreate) -> DoughType:
        return DoughType(
            name=data.name,
            sort_order=data.sort_order,
            is_active=data.is_active,
        )
