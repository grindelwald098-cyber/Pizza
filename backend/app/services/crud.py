"""Одинаковый CRUD справочников: чтение, сборка сущности, вставка, удаление."""

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Generic, TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import Base
from app.exceptions import NotFoundError
from app.repositories.base import BaseRepository

ModelT = TypeVar("ModelT", bound=Base)
CreateT = TypeVar("CreateT")


class CrudService(ABC, Generic[ModelT, CreateT]):
    """Наследник задаёт репозиторий, текст 404 и сборку модели из схемы."""

    repository_cls: ClassVar[type[BaseRepository[Any]]]
    not_found_detail: ClassVar[str]

    def __init__(self, session: AsyncSession) -> None:
        repository_cls = getattr(type(self), "repository_cls", None)
        not_found_detail = getattr(type(self), "not_found_detail", None)
        if repository_cls is None or not isinstance(not_found_detail, str):
            raise TypeError(
                f"{type(self).__name__} must define repository_cls and not_found_detail"
            )
        self.repository: BaseRepository[ModelT] = repository_cls(session)
        self.not_found_detail = not_found_detail

    @abstractmethod
    def build(self, data: CreateT) -> ModelT:
        """Собрать модель из схемы создания. Поля схемы здесь, не в базовом классе."""

    async def get_by_id(self, entity_id: UUID) -> ModelT:
        entity = await self.repository.get_by_id(entity_id)
        if entity is None:
            raise NotFoundError(self.not_found_detail)
        return entity

    async def get_all(self) -> list[ModelT]:
        return await self.repository.get_all()

    async def create(self, data: CreateT) -> ModelT:
        return await self.repository.create(self.build(data))

    async def delete(self, entity_id: UUID) -> None:
        entity = await self.get_by_id(entity_id)
        await self.repository.delete(entity)
