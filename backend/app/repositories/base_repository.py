from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from app.models.base import BaseEntity

ModelType = TypeVar("ModelType", bound=BaseEntity)


class BaseRepository(Generic[ModelType]):
    

    def __init__(self, model: type[ModelType]):
        self.model = model

    def create(self, db: Session, obj: ModelType) -> ModelType:
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def get_by_id(self, db: Session, entity_id: int) -> ModelType | None:
        return (
            db.query(self.model)
            .filter(self.model.id == entity_id)
            .first()
        )

    def get_all(self, db: Session) -> list[ModelType]:
        return db.query(self.model).all()

    def update(self, db: Session, obj: ModelType) -> ModelType:
        db.commit()
        db.refresh(obj)
        return obj

    def delete(self, db: Session, obj: ModelType) -> None:
        db.delete(obj)
        db.commit()