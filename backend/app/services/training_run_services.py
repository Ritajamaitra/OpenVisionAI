from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.training_run import TrainingRun


from app.schemas.training_run import (
    TrainingRunCreate,
    TrainingRunUpdate,
)

from app.repositories.training_run_repository import (
    TrainingRunRepository,
)

from app.services.azure.azure_ml_services import (
    AzureMLService,
)

from app.services.dataset_services import (
    DatasetService,
)

from app.services.project_services import (
    ProjectService,
)

from app.services.model_services import (
    ModelService,
)

from app.services.export_services import (
    ExportService,
)

from app.schemas.export import (
    ExportFormat,
)

from app.services.training_run_services import (
    TrainingRunService,
)


class TrainingService:

    def __init__(
        self,
        db: Session,
    ):

        self.db = db

        # --------------------------------------------------
        # Azure ML
        # --------------------------------------------------

        self.azure_service = AzureMLService()

        # --------------------------------------------------
        # Repository
        # --------------------------------------------------

        self.training_repository = (
            TrainingRunRepository(db)
        )

        self.training_run_service = (
            TrainingRunService(
                self.training_repository
            )
        )

        # --------------------------------------------------
        # Domain Services
        # --------------------------------------------------

        self.project_service = ProjectService()

        self.dataset_service = DatasetService()

        self.model_service = ModelService()

        self.export_service = ExportService()

            # ==========================================================
    # Helpers
    # ==========================================================

    def _validate_project(
        self,
        project_id: int,
        current_user: User,
    ):

        return self.project_service.get_project(
            db=self.db,
            project_id=project_id,
            current_user=current_user,
        )


    def _validate_dataset(
        self,
        dataset_id: int,
        current_user: User,
    ):

        return self.dataset_service.get_dataset(
            db=self.db,
            dataset_id=dataset_id,
            current_user=current_user,
        )


    def _export_dataset(
        self,
        dataset_id: int,
        current_user: User,
    ):

        return self.export_service.export_dataset(
            db=self.db,
            dataset_id=dataset_id,
            export_format=ExportFormat.YOLO,
            current_user=current_user,
        )


    def _create_training_run(
        self,
        request: TrainingRunCreate,
    ) -> TrainingRun:

        return self.training_run_service.create_training_run(
            request
        )


    def _update_training_run(
        self,
        azure_run_id: str,
        update: TrainingRunUpdate,
    ):

        return self.training_run_service.update_training_run(
            azure_run_id,
            update,
        )

        # ==========================================================
    # Submit Training
    # ==========================================================

    def submit_training(
        self,
        request: TrainingRequest,
        current_user: User,
    ) -> TrainingResponse:

        # ------------------------------------------------------
        # Validate Project
        # ------------------------------------------------------

        project = self._validate_project(
            request.project_id,
            current_user,
        )

        # ------------------------------------------------------
        # Validate Dataset
        # ------------------------------------------------------

        dataset = self._validate_dataset(
            request.dataset_id,
            current_user,
        )

        # ------------------------------------------------------
        # Export Dataset
        # ------------------------------------------------------

        exported_dataset = self._export_dataset(
            dataset.id,
            current_user,
        )

        # ------------------------------------------------------
        # Submit Azure ML Job
        # ------------------------------------------------------

        job = self.azure_service.submit_training_job(
            dataset_path=exported_dataset.export_path,
            model_name=request.model_name,
            epochs=request.epochs,
            batch_size=request.batch_size,
            learning_rate=request.learning_rate,
        )

        azure_run_id = job.name

        # ------------------------------------------------------
        # Create Training Run
        # ------------------------------------------------------

        training_run = TrainingRunCreate(

            project_id=project.id,

            dataset_id=dataset.id,

            submitted_by=current_user.id,

            azure_run_id=azure_run_id,

            experiment_name="openvisionai-training",

            model_name=request.model_name,

            status="QUEUED",
        )

        self._create_training_run(
            training_run,
        )

        # ------------------------------------------------------
        # Return
        # ------------------------------------------------------

        return TrainingResponse(

            azure_run_id=azure_run_id,

            status="QUEUED",

            message="Azure ML training job submitted successfully.",

        )

    # ==========================================================
# Sync Training Run
# ==========================================================

def sync_training_run(
    self,
    azure_run_id: str,
):

    training_run = (
        self.training_run_service
        .get_training_run(
            azure_run_id,
        )
    )

    azure = self.azure_service.sync_run(
        azure_run_id,
    )

    metrics = azure.get(
        "metrics",
        {},
    )

    update = TrainingRunUpdate(

        status=azure["status"],

        experiment_name=azure.get(
            "experiment_name"
        ),

        precision=metrics.get(
            "precision"
        ),

        recall=metrics.get(
            "recall"
        ),

        map50=metrics.get(
            "map50"
        ),

        map50_95=metrics.get(
            "map50_95"
        ),

        training_time=metrics.get(
            "training_time"
        ),
    )

    return self.training_run_service.update_training_run(

        azure_run_id,

        update,

    )