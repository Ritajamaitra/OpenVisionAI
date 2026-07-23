from sqlalchemy.orm import Session

from app.models.dataset import Dataset, DatasetStatus
from app.models.user import User
from app.repositories.dataset_repository import DatasetRepository
from app.schemas.dataset import (
    DatasetCreate,
    DatasetUpdate,
)
from app.services.base_services import BaseService
from app.services.project_services import ProjectService


class DatasetService(BaseService[Dataset]):
    """
    Business logic for dataset management.
    """

    def __init__(self):
        super().__init__(DatasetRepository())
        self.project_service = ProjectService()

    def create_dataset(
        self,
        db: Session,
        dataset_data: DatasetCreate,
        project_id: int,
        current_user: User,
    ) -> Dataset:
        """
        Create a dataset under a project owned by the authenticated user.
        """

        project = self.project_service.get_project(
            db=db,
            project_id=project_id,
            current_user=current_user,
        )

        dataset = Dataset(
            name=dataset_data.name,
            description=dataset_data.description,
            project_id=project.id,
            storage_path=dataset_data.storage_path,
            dataset_version=dataset_data.dataset_version,
            total_images=0,
            total_annotations=0,
            status=DatasetStatus.ACTIVE,
        )

        return self.repository.create(
            db=db,
            obj=dataset,
        )

    def get_dataset(
        self,
        db: Session,
        dataset_id: int,
        current_user: User,
    ) -> Dataset:
        """
        Retrieve a dataset only if it belongs to one of the
        authenticated user's projects.
        """

        projects = self.project_service.get_user_projects(
            db=db,
            current_user=current_user,
        )

        for project in projects:
            dataset = self.repository.find_by_id_and_project(
                db=db,
                dataset_id=dataset_id,
                project_id=project.id,
            )

            if dataset is not None:
                return dataset

        raise PermissionError(
            "Dataset not found or access denied."
        )

    def get_project_datasets(
        self,
        db: Session,
        project_id: int,
        current_user: User,
    ) -> list[Dataset]:
        """
        Return every dataset belonging to a project owned
        by the authenticated user.
        """

        project = self.project_service.get_project(
            db=db,
            project_id=project_id,
            current_user=current_user,
        )

        return self.repository.find_by_project(
            db=db,
            project_id=project.id,
        )

    def update_dataset(
        self,
        db: Session,
        dataset_id: int,
        dataset_update: DatasetUpdate,
        current_user: User,
    ) -> Dataset:
        """
        Update only mutable dataset fields.
        """

        dataset = self.get_dataset(
            db=db,
            dataset_id=dataset_id,
            current_user=current_user,
        )

        if dataset_update.name is not None:
            dataset.name = dataset_update.name

        if dataset_update.description is not None:
            dataset.description = dataset_update.description

        if dataset_update.storage_path is not None:
            dataset.storage_path = dataset_update.storage_path

        if dataset_update.dataset_version is not None:
            dataset.dataset_version = dataset_update.dataset_version

        return self.repository.update(
            db=db,
            obj=dataset,
        )

    def delete_dataset(
        self,
        db: Session,
        dataset_id: int,
        current_user: User,
    ) -> None:
        """
        Delete a dataset only if it belongs to one of the
        authenticated user's projects.
        """

        dataset = self.get_dataset(
            db=db,
            dataset_id=dataset_id,
            current_user=current_user,
        )

        self.repository.delete(
            db=db,
            obj=dataset,
        )