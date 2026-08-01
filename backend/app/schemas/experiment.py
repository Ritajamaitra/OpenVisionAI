from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ExperimentStatus(str, Enum):
    """Supported Azure ML experiment run statuses."""

    QUEUED = "Queued"
    PREPARING = "Preparing"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELED = "Canceled"
    NOT_STARTED = "NotStarted"
    FINALIZING = "Finalizing"


class ExperimentSummary(BaseModel):
    """
    Summary information returned when listing experiment runs.
    """

    model_config = ConfigDict(from_attributes=True)

    run_id: str = Field(..., description="Azure ML Job/Run ID")
    experiment_name: str = Field(..., description="Azure ML experiment name")

    project_id: Optional[int] = None
    dataset_id: Optional[int] = None

    model_name: str
    dataset_name: str

    status: ExperimentStatus

    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ExperimentDetails(ExperimentSummary):
    """
    Detailed experiment information.
    """

    epochs: Optional[int] = None
    learning_rate: Optional[float] = None
    batch_size: Optional[int] = None
    image_size: Optional[int] = None

    precision: Optional[float] = None
    recall: Optional[float] = None
    map50: Optional[float] = Field(
        default=None,
        alias="mAP50",
        description="Mean Average Precision @ IoU=0.50",
    )

    map50_95: Optional[float] = Field(
        default=None,
        alias="mAP50_95",
        description="Mean Average Precision @ IoU=0.50:0.95",
    )

    training_time: Optional[str] = None

    registered_model_name: Optional[str] = None
    registered_model_version: Optional[str] = None

    azure_job_url: Optional[str] = None

    tags: dict[str, str] = Field(default_factory=dict)