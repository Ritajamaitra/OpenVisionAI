"""
OpenVisionAI Training Orchestration Service

Responsibilities
----------------
1. Validate project ownership
2. Validate dataset ownership and project relationship
3. Export the dataset to YOLO format
4. Build the Azure ML training request
5. Submit the Azure ML training job
6. Persist the Azure ML run in the database
7. Synchronize Azure ML status and metrics
8. Expose CRUD/lifecycle operations for training runs

The service deliberately does not use the Azure ML SDK directly.
All Azure-specific behavior is delegated to the Azure integration layer.
"""

from datetime import datetime
from typing import List

from sqlalchemy.orm import Session
from app.config.settings import Settings
from app.integrations.azureml.azure_ml import azure_ml
from app.integrations.azureml.contracts import TrainingJobRequest
from app.models.training_run import TrainingRun
from app.models.user import User
from app.repositories.training_run_repository import TrainingRunRepository
from app.schemas.export import ExportFormat
from app.schemas.training_run import TrainingRunCreate, TrainingRunUpdate
from app.services.dataset_services import DatasetService
from app.services.export_services import ExportService
from app.services.project_services import ProjectService


# ==========================================================
# Exceptions
# ==========================================================


class TrainingRunNotFoundException(Exception):
    """Raised when a training run cannot be found."""


class TrainingRunAlreadyExistsException(Exception):
    """Raised when a training run already exists."""


class TrainingSubmissionException(Exception):
    """Raised when Azure ML training submission fails."""


# ==========================================================
# Training Service
# ==========================================================


class TrainingService:
    """
    Orchestrates the complete OpenVisionAI training workflow.

    Flow
    ----
    Project
        ↓
    Dataset
        ↓
    YOLO Export
        ↓
    Azure ML TrainingJobRequest
        ↓
    AzureJobsClient
        ↓
    Azure ML
        ↓
    TrainingRun database record
    """

    DEFAULT_ENVIRONMENT = "openvisionai-yolo-env"
    DEFAULT_ENVIRONMENT_VERSION = "1"
    DEFAULT_COMPUTE = "openvisionai-cpu"
    DEFAULT_EXPERIMENT = "openvisionai-training"

    def __init__(self, db: Session):
        self.db = db

        self.project_service = ProjectService()
        self.dataset_service = DatasetService()
        self.export_service = ExportService()

        self.training_repository = TrainingRunRepository(db)

        # Azure integration facade.
        self.azure_jobs = azure_ml.jobs
        self.azure_monitoring = azure_ml.monitoring

    # ==========================================================
    # Validation
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

    def _validate_project_dataset(
        self,
        project,
        dataset,
    ) -> None:
        """
        Ensure the selected dataset actually belongs to the
        selected project.

        Both resources are independently ownership-checked before
        this relationship check is performed.
        """
        if dataset.project_id != project.id:
            raise PermissionError(
                "Dataset does not belong to the specified project."
            )

    # ==========================================================
    # Dataset Export
    # ==========================================================

    def _export_dataset(
        self,
        dataset_id: int,
        current_user: User,
    ):
        """
        Export the dataset as a YOLO ZIP.

        ExportService owns the Blob Storage and export-format logic.
        """
        return self.export_service.export_dataset(
            db=self.db,
            dataset_id=dataset_id,
            export_format=ExportFormat.YOLO,
            current_user=current_user,
        )

    # ==========================================================
    # Database Record Creation
    # ==========================================================

    def _create_training_record(
        self,
        request: TrainingRunCreate,
    ) -> TrainingRun:
        if self.training_repository.exists(request.azure_run_id):
            raise TrainingRunAlreadyExistsException(
                f"Training run '{request.azure_run_id}' already exists."
            )

        return self.training_repository.create(request)

    # ==========================================================
    # Status Normalization
    # ==========================================================

    @staticmethod
    def _normalize_status(status: str | None) -> str:
        """
        Normalize Azure ML status values to the uppercase values
        used by the TrainingRun repository.

        Examples:
            Running   -> RUNNING
            Completed -> COMPLETED
            Failed    -> FAILED
            Canceled  -> CANCELED
        """
        if not status:
            return "QUEUED"

        normalized = status.strip().upper()

        if normalized == "CANCELLED":
            return "CANCELED"

        return normalized

    # ==========================================================
    # Submit Training
    # ==========================================================

    def submit_training(
        self,
        project_id: int,
        dataset_id: int,
        model_name: str,
        epochs: int,
        imgsz: int,
        batch: int,
        current_user: User,
    ) -> TrainingRun:
        """
        Execute the complete training orchestration workflow.

        1. Validate project
        2. Validate dataset
        3. Validate project/dataset relationship
        4. Export dataset to YOLO
        5. Build Azure ML request
        6. Submit job
        7. Persist TrainingRun
        """

        # ------------------------------------------------------
        # 1. Validate project ownership
        # ------------------------------------------------------
        project = self._validate_project(
            project_id=project_id,
            current_user=current_user,
        )

        # ------------------------------------------------------
        # 2. Validate dataset ownership
        # ------------------------------------------------------
        dataset = self._validate_dataset(
            dataset_id=dataset_id,
            current_user=current_user,
        )

        # ------------------------------------------------------
        # 3. Validate project/dataset relationship
        # ------------------------------------------------------
        self._validate_project_dataset(
            project=project,
            dataset=dataset,
        )

        # ------------------------------------------------------
        # 4. Export dataset to YOLO
        # ------------------------------------------------------
        exported_dataset = self._export_dataset(
            dataset_id=dataset.id,
            current_user=current_user,
        )

        dataset_uri = getattr(
            exported_dataset,
            "download_url",
            None,
        )

        if not dataset_uri:
            raise TrainingSubmissionException(
                "Dataset export did not return a download URL."
            )

        # ------------------------------------------------------
        # 5. Build Azure ML training request
        # ------------------------------------------------------
        #
        # IMPORTANT:
        # TrainingJobRequest uses `compute` and `environment`.
        # Do not use the old environment_name/environment_version/
        # compute_name fields here.
        #
        training_request = TrainingJobRequest(
    experiment_name=self.DEFAULT_EXPERIMENT,
    display_name=f"{model_name}-dataset-{dataset.id}",
    dataset_uri=dataset_uri,
    model_name=model_name,
    epochs=epochs,
    imgsz=imgsz,
    batch=batch,
    compute=self.DEFAULT_COMPUTE,
    environment=(
        f"{self.DEFAULT_ENVIRONMENT}:"
        f"{self.DEFAULT_ENVIRONMENT_VERSION}"
    ),
)

        # ------------------------------------------------------
        # 6. Submit Azure ML job
        # ------------------------------------------------------
        try:
            job = self.azure_jobs.submit_training_job(
                training_request
            )

        except Exception as exc:
            raise TrainingSubmissionException(
                f"Azure ML training submission failed: {exc}"
            ) from exc

        if job is None or not getattr(job, "name", None):
            raise TrainingSubmissionException(
                "Azure ML returned no valid job identifier."
            )

        # ------------------------------------------------------
        # 7. Persist TrainingRun
        # ------------------------------------------------------
        training_record = TrainingRunCreate(
            project_id=project.id,
            dataset_id=dataset.id,
            submitted_by=current_user.id,
            azure_run_id=job.name,
            experiment_name=getattr(
                job,
                "experiment_name",
                self.DEFAULT_EXPERIMENT,
            ),
            model_name=model_name,
            status=self._normalize_status(
                getattr(job, "status", None)
            ),
        )

        return self._create_training_record(
            training_record
        )

    # ==========================================================
    # Synchronize Training Run
    # ==========================================================

    def sync_training_run(
        self,
        azure_run_id: str,
    ) -> TrainingRun:
        """
        Synchronize one database TrainingRun with its Azure ML job.
        """

        training_run = self.get_training_run(
            azure_run_id
        )

        azure_status = self.azure_monitoring.get_status(
            azure_run_id
        )

        status = self._normalize_status(
            azure_status
        )

        update_data = {
            "status": status,
        }

        # ------------------------------------------------------
        # Running
        # ------------------------------------------------------
        if status == "RUNNING":
            update_data["started_at"] = (
                training_run.started_at
                or datetime.utcnow()
            )

        # ------------------------------------------------------
        # Completed
        # ------------------------------------------------------
        elif status == "COMPLETED":
            update_data["completed_at"] = (
                training_run.completed_at
                or datetime.utcnow()
            )

            try:
                metrics = self.azure_monitoring.get_metrics(
                    azure_run_id
                )

                update_data.update(
                    {
                        "precision": getattr(
                            metrics,
                            "precision",
                            None,
                        ),
                        "recall": getattr(
                            metrics,
                            "recall",
                            None,
                        ),
                        "map50": getattr(
                            metrics,
                            "map50",
                            None,
                        ),
                        "map50_95": getattr(
                            metrics,
                            "map50_95",
                            None,
                        ),
                        "training_time": getattr(
                            metrics,
                            "training_time",
                            None,
                        ),
                    }
                )

            except Exception:
                # Metrics are optional at synchronization time.
                # The job status should still be persisted.
                pass

        # ------------------------------------------------------
        # Failed / Cancelled
        # ------------------------------------------------------
        elif status in {
            "FAILED",
            "CANCELED",
        }:
            update_data["completed_at"] = (
                training_run.completed_at
                or datetime.utcnow()
            )

        # ------------------------------------------------------
        # Persist synchronization
        # ------------------------------------------------------
        return self.update_training_run(
            azure_run_id=azure_run_id,
            update=TrainingRunUpdate(**update_data),
        )

    # ==========================================================
    # Get
    # ==========================================================

    def get_training_run(
        self,
        azure_run_id: str,
    ) -> TrainingRun:
        training_run = self.training_repository.get_by_run_id(
            azure_run_id
        )

        if training_run is None:
            raise TrainingRunNotFoundException(
                f"Training run '{azure_run_id}' not found."
            )

        return training_run

    # ==========================================================
    # List
    # ==========================================================

    def list_training_runs(
        self,
    ) -> List[TrainingRun]:
        return self.training_repository.list()

    # ==========================================================
    # Project Runs
    # ==========================================================

    def list_project_training_runs(
        self,
        project_id: int,
        current_user: User | None = None,
    ) -> List[TrainingRun]:
        """
        Return training runs for a project.

        If current_user is supplied, project ownership is validated
        before querying the repository.
        """
        if current_user is not None:
            self._validate_project(
                project_id=project_id,
                current_user=current_user,
            )

        return self.training_repository.list_by_project(
            project_id
        )

    # ==========================================================
    # Update
    # ==========================================================

    def update_training_run(
        self,
        azure_run_id: str,
        update: TrainingRunUpdate,
    ) -> TrainingRun:
        training_run = self.get_training_run(
            azure_run_id
        )

        return self.training_repository.update(
            training_run,
            update,
        )

    # ==========================================================
    # Cancel Azure Job
    # ==========================================================

    def cancel_training_run(
        self,
        azure_run_id: str,
    ) -> TrainingRun:
        """
        Cancel the Azure ML job and synchronize the local record.
        """

        self.get_training_run(
            azure_run_id
        )

        try:
            self.azure_jobs.cancel_job(
                azure_run_id
            )
        except Exception as exc:
            raise TrainingSubmissionException(
                f"Failed to cancel Azure ML job "
                f"'{azure_run_id}': {exc}"
            ) from exc

        return self.update_training_run(
            azure_run_id=azure_run_id,
            update=TrainingRunUpdate(
                status="CANCELED",
                completed_at=datetime.utcnow(),
            ),
        )

    # ==========================================================
    # Delete
    # ==========================================================

    def delete_training_run(
        self,
        azure_run_id: str,
    ) -> None:
        training_run = self.get_training_run(
            azure_run_id
        )

        self.training_repository.delete(
            training_run
        )

    # ==========================================================
    # Convenience Queries
    # ==========================================================

    def running_jobs(self) -> List[TrainingRun]:
        return self.training_repository.running()

    def completed_jobs(self) -> List[TrainingRun]:
        return self.training_repository.completed()

    def failed_jobs(self) -> List[TrainingRun]:
        return self.training_repository.failed()