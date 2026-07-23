from sqlalchemy.orm import Session

from app.models.model_registry import (
    ModelRegistry,
    ModelStatus,
)
from app.models.user import User
from app.repositories.model_repository import ModelRepository
from app.schemas.model import (
    ModelCreate,
    ModelUpdate,
)
from app.services.base_services import BaseService
from app.services.dataset_services import DatasetService


class ModelService(BaseService[ModelRegistry]):
    """
    Business logic for Model Registry management.
    """

    def __init__(self):
        super().__init__(ModelRepository())
        self.dataset_service = DatasetService()

    def create_model(
        self,
        db: Session,
        model_data: ModelCreate,
        dataset_id: int,
        current_user: User,
    ) -> ModelRegistry:
        """
        Create a model under a dataset owned by the authenticated user.
        """

        dataset = self.dataset_service.get_dataset(
            db=db,
            dataset_id=dataset_id,
            current_user=current_user,
        )

        model = ModelRegistry(
            name=model_data.name,
            description=model_data.description,
            dataset_id=dataset.id,
            model_type=model_data.model_type,
            framework=model_data.framework,
            version=model_data.version,
            mlflow_run_id=model_data.mlflow_run_id,
            artifact_uri=model_data.artifact_uri,
            metrics_json=model_data.metrics_json,
            status=ModelStatus.ACTIVE,
        )

        return self.repository.create(
            db=db,
            obj=model,
        )

    def get_model(
        self,
        db: Session,
        model_id: int,
        current_user: User,
    ) -> ModelRegistry:
        """
        Retrieve a model only if it belongs to one of the
        authenticated user's datasets.
        """

        projects = self.dataset_service.project_service.get_user_projects(
            db=db,
            current_user=current_user,
        )

        for project in projects:

            datasets = self.dataset_service.get_project_datasets(
                db=db,
                project_id=project.id,
                current_user=current_user,
            )

            for dataset in datasets:

                model = self.repository.find_by_id_and_dataset(
                    db=db,
                    model_id=model_id,
                    dataset_id=dataset.id,
                )

                if model is not None:
                    return model

        raise PermissionError(
            "Model not found or access denied."
        )

    def get_dataset_models(
        self,
        db: Session,
        dataset_id: int,
        current_user: User,
    ) -> list[ModelRegistry]:
        """
        Return all models belonging to a dataset.
        """

        dataset = self.dataset_service.get_dataset(
            db=db,
            dataset_id=dataset_id,
            current_user=current_user,
        )

        return self.repository.find_by_dataset(
            db=db,
            dataset_id=dataset.id,
        )

    def update_model(
        self,
        db: Session,
        model_id: int,
        model_update: ModelUpdate,
        current_user: User,
    ) -> ModelRegistry:
        """
        Update mutable model fields.
        """

        model = self.get_model(
            db=db,
            model_id=model_id,
            current_user=current_user,
        )

        if model_update.name is not None:
            model.name = model_update.name

        if model_update.description is not None:
            model.description = model_update.description

        if model_update.model_type is not None:
            model.model_type = model_update.model_type

        if model_update.framework is not None:
            model.framework = model_update.framework

        if model_update.version is not None:
            model.version = model_update.version

        if model_update.mlflow_run_id is not None:
            model.mlflow_run_id = model_update.mlflow_run_id

        if model_update.artifact_uri is not None:
            model.artifact_uri = model_update.artifact_uri

        if model_update.metrics_json is not None:
            model.metrics_json = model_update.metrics_json

        return self.repository.update(
            db=db,
            obj=model,
        )

    def delete_model(
        self,
        db: Session,
        model_id: int,
        current_user: User,
    ) -> None:
        """
        Delete a model owned by the authenticated user.
        """

        model = self.get_model(
            db=db,
            model_id=model_id,
            current_user=current_user,
        )

        self.repository.delete(
            db=db,
            obj=model,
        )