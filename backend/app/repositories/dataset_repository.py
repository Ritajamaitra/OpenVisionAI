from sqlalchemy.orm import Session

from app.models.dataset import Dataset, DatasetStatus
from app.repositories.base_repository import BaseRepository


class DatasetRepository(BaseRepository[Dataset]):
    """
    Repository for Dataset-specific database operations.
    """

    def __init__(self):
        super().__init__(Dataset)

    def find_by_project(
        self,
        db: Session,
        project_id: int,
    ) -> list[Dataset]:
        """
        Retrieve all datasets belonging to a project.
        """

        return (
            db.query(Dataset)
            .filter(Dataset.project_id == project_id)
            .order_by(Dataset.created_at.desc())
            .all()
        )

    def find_active_datasets(
        self,
        db: Session,
    ) -> list[Dataset]:
        """
        Retrieve all active datasets.
        """

        return (
            db.query(Dataset)
            .filter(Dataset.status == DatasetStatus.ACTIVE)
            .order_by(Dataset.created_at.desc())
            .all()
        )

    def find_by_id_and_project(
        self,
        db: Session,
        dataset_id: int,
        project_id: int,
    ) -> Dataset | None:
        """
        Retrieve a dataset only if it belongs to the specified project.
        """

        return (
            db.query(Dataset)
            .filter(
                Dataset.id == dataset_id,
                Dataset.project_id == project_id,
            )
            .first()
        )