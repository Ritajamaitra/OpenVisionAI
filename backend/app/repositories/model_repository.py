from sqlalchemy.orm import Session

from app.models.model_registry import (
    ModelRegistry,
    ModelStatus,
)
from app.repositories.base_repository import BaseRepository


class ModelRepository(BaseRepository[ModelRegistry]):
    """
    Repository for Model Registry specific database operations.
    """

    def __init__(self):
        super().__init__(ModelRegistry)

    def find_by_dataset(
        self,
        db: Session,
        dataset_id: int,
    ) -> list[ModelRegistry]:
        """
        Retrieve all models belonging to a dataset.
        """

        return (
            db.query(ModelRegistry)
            .filter(
                ModelRegistry.dataset_id == dataset_id
            )
            .order_by(ModelRegistry.created_at.desc())
            .all()
        )

    def find_active_models(
        self,
        db: Session,
    ) -> list[ModelRegistry]:
        """
        Retrieve all active models.
        """

        return (
            db.query(ModelRegistry)
            .filter(
                ModelRegistry.status == ModelStatus.ACTIVE
            )
            .order_by(ModelRegistry.created_at.desc())
            .all()
        )

    def find_by_id_and_dataset(
        self,
        db: Session,
        model_id: int,
        dataset_id: int,
    ) -> ModelRegistry | None:
        """
        Retrieve a model only if it belongs to
        the specified dataset.
        """

        return (
            db.query(ModelRegistry)
            .filter(
                ModelRegistry.id == model_id,
                ModelRegistry.dataset_id == dataset_id,
            )
            .first()
        )