from sqlalchemy.orm import Session

from app.models.model_registry import ModelRegistry
from app.models.model_status import ModelStatus
from app.repositories.base_repository import BaseRepository


class ModelRepository(BaseRepository[ModelRegistry]):
    def __init__(self):
        super().__init__(ModelRegistry)

    def find_by_dataset(
        self,
        db: Session,
        dataset_id: int,
    ) -> list[ModelRegistry]:
        return (
            db.query(ModelRegistry)
            .filter(ModelRegistry.dataset_id == dataset_id)
            .all()
        )

    def find_active_models(
        self,
        db: Session,
    ) -> list[ModelRegistry]:
        return (
            db.query(ModelRegistry)
            .filter(ModelRegistry.status == ModelStatus.ACTIVE)
            .all()
        )