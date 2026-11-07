
from typing import Any, ClassVar, Generic, TypeVar, cast
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from app.database.database import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    model: ClassVar[type[ModelT]]

    def __init__(self, session: AsyncSession) -> None:
        if getattr(type(self), "model", None) is None:
            raise TypeError(
                f"{type(self).__name__} must define class attribute model"
            )
        self.session = session

    @staticmethod
    def _load_options() -> tuple[Any, ...]:
        return ()

    def _id_column(self) -> ColumnElement[Any]:
        return cast(ColumnElement[Any], getattr(self.model, "id"))

    def _select(self) -> Select[tuple[ModelT]]:
        statement = select(self.model)
        options = self._load_options()
        if options:
            statement = statement.options(*options)
        return statement

    async def _list(self, statement: Select[tuple[ModelT]]) -> list[ModelT]:
        result = await self.session.scalars(statement)
        return list(result.all())

    async def _persist(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def get_all(self) -> list[ModelT]:
        return await self._list(self._select())

    async def get_by_id(self, entity_id: UUID) -> ModelT | None:
        statement = self._select().where(self._id_column() == entity_id)
        return await self.session.scalar(statement)

    async def get_existing_ids(self, ids: list[UUID]) -> set[UUID]:
        if not ids:
            return set()

        id_column = self._id_column()
        statement = select(id_column).where(id_column.in_(ids))
        result = await self.session.scalars(statement)
        return set(result.all())

    async def get_by_ids(self, ids: list[UUID]) -> list[ModelT]:
        if not ids:
            return []

        statement = self._select().where(self._id_column().in_(ids))
        return await self._list(statement)

    async def get_one_by(self, **equals: object) -> ModelT | None:
        conditions = [
            getattr(self.model, field) == value
            for field, value in equals.items()
        ]
        return await self.session.scalar(self._select().where(*conditions))

    async def create(self, entity: ModelT) -> ModelT:
        return await self._persist(entity)

    async def create_many(self, entities: list[ModelT]) -> list[ModelT]:
        self.session.add_all(entities)
        await self.session.flush()
        return entities

    async def update(self, entity: ModelT) -> ModelT:
        return await self._persist(entity)

    async def delete(self, entity: ModelT) -> None:
        await self.session.delete(entity)
        await self.session.flush()


class SoftDeleteRepository(BaseRepository[ModelT]):

    async def deactivate(self, entity: ModelT) -> ModelT:
        if not hasattr(entity, "is_active"):
            raise TypeError(f"{type(entity).__name__} has no is_active")
        setattr(entity, "is_active", False)
        return await self._persist(entity)
