from __future__ import annotations

from datetime import datetime
from typing import Optional

from azure.ai.ml import MLClient
from azure.core.exceptions import ResourceNotFoundError

from app.schemas.experiment import (
    ExperimentDetails,
    ExperimentStatus,
    ExperimentSummary,
)


class ExperimentNotFoundException(Exception):
    """Raised when an Azure ML experiment/job cannot be found."""

    pass


class ExperimentService:
    """
    Service responsible for retrieving Azure ML experiment (job) metadata.

    This service isolates Azure ML SDK interactions from the API layer.
    """

    def __init__(self, ml_client: MLClient):
        self.ml_client = ml_client

    # ------------------------------------------------------------------
    # Public Methods
    # ------------------------------------------------------------------

    def list_experiments(
        self,
        project_id: Optional[int] = None,
    ) -> list[ExperimentSummary]:
        """
        Retrieve all Azure ML experiment runs.

        If project_id is provided, results are filtered using Azure ML tags.
        """

        experiments: list[ExperimentSummary] = []

        for job in self.ml_client.jobs.list():

            tags = job.tags or {}

            if (
                project_id is not None
                and str(project_id) != tags.get("project_id")
            ):
                continue

            experiments.append(self._build_summary(job))

        return experiments

    def get_experiment(
        self,
        run_id: str,
    ) -> ExperimentDetails:
        """
        Retrieve a single Azure ML experiment by run ID.
        """

        try:
            job = self.ml_client.jobs.get(run_id)

        except ResourceNotFoundError as exc:
            raise ExperimentNotFoundException(
                f"Experiment '{run_id}' not found."
            ) from exc

        return self._build_details(job)

    # ------------------------------------------------------------------
    # Private Mapping Methods
    # ------------------------------------------------------------------

    def _build_summary(self, job) -> ExperimentSummary:
        """
        Convert an Azure ML Job into ExperimentSummary.
        """

        tags = job.tags or {}

        return ExperimentSummary(
            run_id=job.name,
            experiment_name=job.experiment_name,

            project_id=self._to_int(tags.get("project_id")),
            dataset_id=self._to_int(tags.get("dataset_id")),

            model_name=tags.get("model_name", "Unknown"),
            dataset_name=tags.get("dataset_name", "Unknown"),

            status=self._parse_status(job.status),

            started_at=getattr(job, "creation_context", None).created_at
            if getattr(job, "creation_context", None)
            else None,

            completed_at=getattr(job, "creation_context", None).last_modified_at
            if getattr(job, "creation_context", None)
            else None,
        )

    def _build_details(self, job) -> ExperimentDetails:
        """
        Convert an Azure ML Job into ExperimentDetails.
        """

        summary = self._build_summary(job)

        tags = job.tags or {}

        metrics = self._extract_metrics(job)
        params = self._extract_parameters(job)

        return ExperimentDetails(
            **summary.model_dump(),

            epochs=params.get("epochs"),
            batch_size=params.get("batch_size"),
            learning_rate=params.get("learning_rate"),
            image_size=params.get("image_size"),

            precision=metrics.get("precision"),
            recall=metrics.get("recall"),
            map50=metrics.get("mAP50"),
            map50_95=metrics.get("mAP50_95"),

            training_time=metrics.get("training_time"),

            registered_model_name=tags.get("registered_model_name"),
            registered_model_version=tags.get("registered_model_version"),

            azure_job_url=tags.get("azure_job_url"),

            tags=tags,
        )

    # ------------------------------------------------------------------
    # Helper Methods
    # ------------------------------------------------------------------

    def _extract_metrics(self, job) -> dict:
        """
        Extract metrics from Azure ML Job.

        Metrics may later be retrieved from MLflow instead.
        """

        return {
            "precision": None,
            "recall": None,
            "mAP50": None,
            "mAP50_95": None,
            "training_time": None,
        }

    def _extract_parameters(self, job) -> dict:
        """
        Extract training parameters from Azure ML Job inputs.
        """

        inputs = getattr(job, "inputs", {}) or {}

        return {
            "epochs": self._input_value(inputs.get("epochs")),
            "batch_size": self._input_value(inputs.get("batch")),
            "learning_rate": self._input_value(inputs.get("learning_rate")),
            "image_size": self._input_value(inputs.get("imgsz")),
        }

    @staticmethod
    def _input_value(value):
        """
        Azure ML inputs may be Input objects or primitive values.
        """

        if value is None:
            return None

        if hasattr(value, "value"):
            return value.value

        return value

    @staticmethod
    def _parse_status(status: str) -> ExperimentStatus:
        """
        Convert Azure ML status string into ExperimentStatus enum.
        """

        try:
            return ExperimentStatus(status)

        except ValueError:
            return ExperimentStatus.RUNNING

    @staticmethod
    def _to_int(value):
        if value is None:
            return None

        try:
            return int(value)
        except (TypeError, ValueError):
            return None