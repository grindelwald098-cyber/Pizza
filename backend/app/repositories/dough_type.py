from app.database.models.dough_type import DoughType
from app.repositories.base import BaseRepository


class DoughTypeRepository(BaseRepository[DoughType]):
    model = DoughType
