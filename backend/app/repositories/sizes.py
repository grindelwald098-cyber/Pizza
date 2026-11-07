from app.database.models.sizes import Size
from app.repositories.base import BaseRepository


class SizesRepository(BaseRepository[Size]):
    model = Size
