"""
OpenVisionAI Training Orchestration Service

Responsibilities
----------------
1. Validate project ownership
2. Validate dataset ownership and project relationship
3. Resolve Azure ML data/environment assets
4. Submit Azure ML training jobs
5. Persist TrainingRun
6. Synchronize Azure ML status and metrics
7. Automatically register completed model
8. Persist model registry metadata
"""

from datetime import datetime
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.integrations.azureml.azure_ml import azure_ml
from app.integrations.azureml.contracts import TrainingJobRequest
from app.integrations.azureml.registry import AzureRegistryClient

from app.models.training_run import TrainingRun
from app.models.user import User
from app.models.model_registry import ModelRegistry

from app.repositories.training_run_repository import TrainingRunRepository

from app.schemas.training_run import (
    TrainingRunCreate,
    TrainingRunUpdate,
)

from app.services.dataset_services import DatasetService
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


class ModelRegistrationException(Exception):
    """Raised when automatic model registration fails."""


# ==========================================================
# Training Service
# ==========================================================

class TrainingService:
    """Orchestrates the complete OpenVisionAI training workflow."""

    # ------------------------------------------------------
    # Azure ML configuration
    # ------------------------------------------------------

    DEFAULT_ENVIRONMENT = "openvisionai-yolo-env"
    DEFAULT_ENVIRONMENT_VERSION = "1"

    DEFAULT_COMPUTE = "openvisionai-cpu"

    DEFAULT_EXPERIMENT = "openvisionai-training"

    DEFAULT_DATA_ASSET = "openvisionai-yolo-dataset"
    DEFAULT_DATA_ASSET_VERSION = "1"

    # Stable name in Azure ML Model Registry
    DEFAULT_REGISTERED_MODEL_NAME = "openvisionai-yolo"

    # OpenVisionAI model metadata
    DEFAULT_MODEL_TYPE = "object_detection"
    DEFAULT_FRAMEWORK = "Ultralytics YOLO"

    def __init__(self, db: Session):
        self.db = db

        self.project_service = ProjectService()
        self.dataset_service = DatasetService()

        self.training_repository = TrainingRunRepository(db)

        self.azure_jobs = azure_ml.jobs
        self.azure_monitoring = azure_ml.monitoring

        # Azure ML Model Registry
        self.azure_registry = AzureRegistryClient()

    # ======================================================
    # Validation
    # ======================================================

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

    @staticmethod
    def _validate_project_dataset(
        project,
        dataset,
    ) -> None:

        if dataset.project_id != project.id:
            raise PermissionError(
                "Dataset does not belong to the specified project."
            )

    # ======================================================
    # Azure ML Assets
    # ======================================================

    @classmethod
    def _get_dataset_uri(cls) -> str:
        return (
            f"azureml:{cls.DEFAULT_DATA_ASSET}:"
            f"{cls.DEFAULT_DATA_ASSET_VERSION}"
        )

    @classmethod
    def _get_environment_uri(cls) -> str:
        return (
            f"{cls.DEFAULT_ENVIRONMENT}:"
            f"{cls.DEFAULT_ENVIRONMENT_VERSION}"
        )

    # ======================================================
    # Database Record Creation
    # ======================================================

    def _create_training_record(
        self,
        request: TrainingRunCreate,
    ) -> TrainingRun:

        if self.training_repository.exists(
            request.azure_run_id
        ):
            raise TrainingRunAlreadyExistsException(
                f"Training run '{request.azure_run_id}' "
                f"already exists."
            )

        return self.training_repository.create(
            request
        )

    # ======================================================
    # Status Normalization
    # ======================================================

    @staticmethod
    def _normalize_status(
        status: str | None,
    ) -> str:

        if not status:
            return "QUEUED"

        normalized = status.strip().upper()

        if normalized == "CANCELLED":
            return "CANCELED"

        return normalized

    # ======================================================
    # Submit Training
    # ======================================================

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

        # --------------------------------------------------
        # 1. Validate project
        # --------------------------------------------------

        project = self._validate_project(
            project_id=project_id,
            current_user=current_user,
        )

        # --------------------------------------------------
        # 2. Validate dataset
        # --------------------------------------------------

        dataset = self._validate_dataset(
            dataset_id=dataset_id,
            current_user=current_user,
        )

        # --------------------------------------------------
        # 3. Validate relationship
        # --------------------------------------------------

        self._validate_project_dataset(
            project=project,
            dataset=dataset,
        )

        # --------------------------------------------------
        # 4. Azure ML assets
        # --------------------------------------------------

        dataset_uri = self._get_dataset_uri()
        environment_uri = self._get_environment_uri()

        # --------------------------------------------------
        # 5. Build training request
        # --------------------------------------------------

        training_request = TrainingJobRequest(
            experiment_name=self.DEFAULT_EXPERIMENT,

            display_name=(
                f"{model_name}-dataset-{dataset.id}"
            ),

            dataset_uri=dataset_uri,

            model_name=model_name,

            epochs=epochs,

            imgsz=imgsz,

            batch=batch,

            compute=self.DEFAULT_COMPUTE,

            environment=environment_uri,
        )

        # --------------------------------------------------
        # 6. Submit Azure ML job
        # --------------------------------------------------

        try:

            job = self.azure_jobs.submit_training_job(
                training_request
            )

        except Exception as exc:

            raise TrainingSubmissionException(
                f"Azure ML training submission failed: {exc}"
            ) from exc

        if job is None or not getattr(
            job,
            "name",
            None,
        ):

            raise TrainingSubmissionException(
                "Azure ML returned no valid job identifier."
            )

        # --------------------------------------------------
        # 7. Persist TrainingRun
        # --------------------------------------------------

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
                getattr(
                    job,
                    "status",
                    None,
                )
            ),
        )

        return self._create_training_record(
            training_record
        )

    # ======================================================
    # Automatic Model Registration
    # ======================================================

    def _register_completed_model(
        self,
        training_run: TrainingRun,
        metrics,
    ) -> tuple[str, str]:

        azure_run_id = training_run.azure_run_id

        # --------------------------------------------------
        # Prevent duplicate registration
        # --------------------------------------------------

        if (
            training_run.registered_model_name
            and training_run.registered_model_version
        ):
            return (
                training_run.registered_model_name,
                training_run.registered_model_version,
            )

        # --------------------------------------------------
        # Azure ML registration
        # --------------------------------------------------

        registered_name = self.DEFAULT_REGISTERED_MODEL_NAME

        try:

            registered_model = (
                self.azure_registry.register_job_output(
                    job_name=azure_run_id,
                    registered_name=registered_name,
                    description=(
                        "OpenVisionAI YOLO object detection "
                        f"model trained from Azure ML job "
                        f"{azure_run_id}."
                    ),
                )
            )

        except Exception as exc:

            raise ModelRegistrationException(
                "Automatic Azure ML model registration "
                f"failed for job '{azure_run_id}': {exc}"
            ) from exc

        model_name = registered_model.name
        model_version = str(
            registered_model.version
        )

        # --------------------------------------------------
        # Build metrics payload
        # --------------------------------------------------

        metrics_json = {
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
            "azure_run_id": azure_run_id,
        }

        # --------------------------------------------------
        # Artifact provenance
        # --------------------------------------------------

        artifact_uri = (
            f"azureml://jobs/{azure_run_id}"
            "/outputs/models/best.pt"
        )

        # --------------------------------------------------
        # Check whether DB registry entry exists
        # --------------------------------------------------

        existing = self.db.execute(
            select(ModelRegistry).where(
                ModelRegistry.dataset_id
                == training_run.dataset_id,

                ModelRegistry.name
                == model_name,

                ModelRegistry.version
                == model_version,
            )
        ).scalar_one_or_none()

        if existing is None:

            registry_record = ModelRegistry(
                name=model_name,

                description=(
                    "OpenVisionAI YOLO model automatically "
                    "registered from Azure ML."
                ),

                dataset_id=training_run.dataset_id,

                model_type=self.DEFAULT_MODEL_TYPE,

                framework=self.DEFAULT_FRAMEWORK,

                version=model_version,

                mlflow_run_id=None,

                artifact_uri=artifact_uri,

                metrics_json=metrics_json,
            )

            self.db.add(registry_record)

        else:

            existing.artifact_uri = artifact_uri
            existing.metrics_json = metrics_json

        # Make the DB object visible to the current transaction.
        self.db.flush()

        return (
            model_name,
            model_version,
        )

    # ======================================================
    # Synchronize Training Run
    # ======================================================

    def sync_training_run(
        self,
        azure_run_id: str,
    ) -> TrainingRun:

        training_run = self.get_training_run(
            azure_run_id
        )

        # --------------------------------------------------
        # 1. Get Azure status
        # --------------------------------------------------

        azure_status = self.azure_monitoring.get_status(
            azure_run_id
        )

        status = self._normalize_status(
            azure_status
        )

        update_data = {
            "status": status,
        }

        # --------------------------------------------------
        # 2. Running
        # --------------------------------------------------

        if status == "RUNNING":

            update_data["started_at"] = (
                training_run.started_at
                or datetime.utcnow()
            )

        # --------------------------------------------------
        # 3. Completed
        # --------------------------------------------------

        elif status == "COMPLETED":

            update_data["completed_at"] = (
                training_run.completed_at
                or datetime.utcnow()
            )

            try:

                # ------------------------------------------
                # Get metrics
                # ------------------------------------------

                metrics = (
                    self.azure_monitoring.get_metrics(
                        azure_run_id
                    )
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

                # ------------------------------------------
                # Automatic model registration
                # ------------------------------------------

                (
                    registered_name,
                    registered_version,
                ) = self._register_completed_model(
                    training_run=training_run,
                    metrics=metrics,
                )

                update_data.update(
                    {
                        "registered_model_name":
                            registered_name,

                        "registered_model_version":
                            registered_version,
                    }
                )

            except ModelRegistrationException as exc:

                # Training succeeded, but registration
                # failed. Keep COMPLETED status and allow
                # another /sync to retry registration.

                print(
                    f"WARNING: Azure ML job "
                    f"'{azure_run_id}' completed, "
                    f"but model registration failed: "
                    f"{exc}"
                )

            except Exception as exc:

                # Metrics/artifacts may temporarily be
                # unavailable immediately after completion.

                print(
                    f"WARNING: Azure ML job "
                    f"'{azure_run_id}' completed, "
                    f"but synchronization failed: "
                    f"{exc}"
                )

        # --------------------------------------------------
        # 4. Failed / Cancelled
        # --------------------------------------------------

        elif status in {
            "FAILED",
            "CANCELED",
        }:

            update_data["completed_at"] = (
                training_run.completed_at
                or datetime.utcnow()
            )

        # --------------------------------------------------
        # 5. Persist everything
        # --------------------------------------------------

        return self.update_training_run(
            azure_run_id=azure_run_id,

            update=TrainingRunUpdate(
                **update_data
            ),
        )

    # ======================================================
    # Get Training Run
    # ======================================================

    def get_training_run(
        self,
        azure_run_id: str,
    ) -> TrainingRun:

        training_run = (
            self.training_repository.get_by_run_id(
                azure_run_id
            )
        )

        if training_run is None:

            raise TrainingRunNotFoundException(
                f"Training run '{azure_run_id}' not found."
            )

        return training_run

    # ======================================================
    # List Training Runs
    # ======================================================

    def list_training_runs(
        self,
    ) -> List[TrainingRun]:

        return self.training_repository.list()

    # ======================================================
    # Project Training Runs
    # ======================================================

    def list_project_training_runs(
        self,
        project_id: int,
        current_user: User | None = None,
    ) -> List[TrainingRun]:

        if current_user is not None:

            self._validate_project(
                project_id=project_id,
                current_user=current_user,
            )

        return self.training_repository.list_by_project(
            project_id
        )

    # ======================================================
    # Update Training Run
    # ======================================================

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

    # ======================================================
    # Cancel
    # ======================================================

    def cancel_training_run(
        self,
        azure_run_id: str,
    ) -> TrainingRun:

        self.get_training_run(
            azure_run_id
        )

        try:

            self.azure_jobs.cancel_job(
                azure_run_id
            )

        except Exception as exc:

            raise TrainingSubmissionException(
                "Failed to cancel Azure ML training run "
                f"'{azure_run_id}': {exc}"
            ) from exc

        return self.update_training_run(
            azure_run_id=azure_run_id,

            update=TrainingRunUpdate(
                status="CANCELED",
                completed_at=datetime.utcnow(),
            ),
        )

    # ======================================================
    # Delete
    # ======================================================

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

    # ======================================================
    # Convenience Queries
    # ======================================================

    def running_jobs(
        self,
    ) -> List[TrainingRun]:

        return self.training_repository.running()

    def completed_jobs(
        self,
    ) -> List[TrainingRun]:

        return self.training_repository.completed()

    def failed_jobs(
        self,
    ) -> List[TrainingRun]:

        return self.training_repository.failed()