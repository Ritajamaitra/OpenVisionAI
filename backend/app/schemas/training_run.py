from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ==========================================================
# Base Schema
# ==========================================================

class TrainingRunBase(BaseModel):

    project_id: int
    dataset_id: int
    submitted_by: int

    azure_run_id: str

    experiment_name: Optional[str] = None
    model_name: Optional[str] = None

    status: str = "QUEUED"

    precision: Optional[float] = None
    recall: Optional[float] = None
    map50: Optional[float] = None
    map50_95: Optional[float] = None

    training_time: Optional[float] = None

    registered_model_name: Optional[str] = None
    registered_model_version: Optional[str] = None

    endpoint_name: Optional[str] = None


# ==========================================================
# Create
# ==========================================================

class TrainingRunCreate(TrainingRunBase):
    pass


# ==========================================================
# Update
# ==========================================================

class TrainingRunUpdate(BaseModel):

    experiment_name: Optional[str] = None
    model_name: Optional[str] = None

    status: Optional[str] = None

    precision: Optional[float] = None
    recall: Optional[float] = None
    map50: Optional[float] = None
    map50_95: Optional[float] = None

    training_time: Optional[float] = None

    registered_model_name: Optional[str] = None
    registered_model_version: Optional[str] = None

    endpoint_name: Optional[str] = None

    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# ==========================================================
# Response
# ==========================================================

class TrainingRunResponse(TrainingRunBase):

    id: int

    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================================
# Summary
# ==========================================================

class TrainingRunSummary(BaseModel):

    azure_run_id: str

    project_id: int

    experiment_name: Optional[str]

    model_name: Optional[str]

    status: str

    precision: Optional[float]

    recall: Optional[float]

    map50: Optional[float]

    map50_95: Optional[float]

    model_config = ConfigDict(from_attributes=True)