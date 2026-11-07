from app.database.models.sizes import Size
from app.repositories.sizes import SizesRepository
from app.schemas.sizes import SizeCreate
from app.services.crud import CrudService


class SizesService(CrudService[Size, SizeCreate]):
    repository_cls = SizesRepository
    not_found_detail = "Size not found"

    def build(self, data: SizeCreate) -> Size:
        return Size(
            name=data.name,
            value=data.value,
            unit=data.unit,
            sort_order=data.sort_order,
        )

    async def get_all(self) -> list[Size]:
        sizes = await super().get_all()
        sizes.sort(key=lambda size: size.sort_order)
        return sizes
