from sqlalchemy.orm import Session

from app.models.dataset import Dataset
from app.models.dataset_status import DatasetStatus
from app.repositories.base_repository import BaseRepository


class DatasetRepository(BaseRepository[Dataset]):
    def __init__(self):
        super().__init__(Dataset)

    def find_by_project(
        self,
        db: Session,
        project_id: int,
    ) -> list[Dataset]:
        return (
            db.query(Dataset)
            .filter(Dataset.project_id == project_id)
            .all()
        )

    def find_active_datasets(
        self,
        db: Session,
    ) -> list[Dataset]:
        return (
            db.query(Dataset)
            .filter(Dataset.status == DatasetStatus.ACTIVE)
            .all()
        )