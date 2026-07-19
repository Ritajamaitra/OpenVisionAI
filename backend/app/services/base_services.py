from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from app.models.base import BaseEntity
from app.repositories.base_repository import BaseRepository

ModelType = TypeVar("ModelType", bound=BaseEntity)


class BaseService(Generic[ModelType]):
    """
    Base service containing generic business operations.
    Delegates persistence to repositories.
    """

    def __init__(self, repository: BaseRepository[ModelType]):
        self.repository = repository

    def create(self, db: Session, entity: ModelType) -> ModelType:
        return self.repository.create(db, entity)

    def get_by_id(self, db: Session, entity_id: int) -> ModelType | None:
        return self.repository.get_by_id(db, entity_id)

    def get_all(self, db: Session) -> list[ModelType]:
        return self.repository.get_all(db)

    def update(self, db: Session, entity: ModelType) -> ModelType:
        return self.repository.update(db, entity)

    def delete(self, db: Session, entity: ModelType) -> None:
        self.repository.delete(db, entity)