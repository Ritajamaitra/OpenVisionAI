from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.model_registry import ModelStatus


class ModelCreate(BaseModel):
    """
    Request schema for creating a model registry entry.
    """

    name: str = Field(
        min_length=3,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    model_type: str = Field(
        min_length=2,
        max_length=100,
    )

    framework: str = Field(
        min_length=2,
        max_length=100,
    )

    version: str = Field(
        min_length=1,
        max_length=50,
    )

    mlflow_run_id: str | None = Field(
        default=None,
        max_length=255,
    )

    artifact_uri: str = Field(
        min_length=1,
        max_length=1024,
    )

    metrics_json: dict[str, Any] | None = None


class ModelUpdate(BaseModel):
    """
    Request schema for updating model metadata.
    """

    name: str | None = Field(
        default=None,
        min_length=3,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    model_type: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    framework: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    version: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    mlflow_run_id: str | None = Field(
        default=None,
        max_length=255,
    )

    artifact_uri: str | None = Field(
        default=None,
        min_length=1,
        max_length=1024,
    )

    metrics_json: dict[str, Any] | None = None


class ModelResponse(BaseModel):
    """
    Response schema returned to API clients.
    """

    id: int

    name: str

    description: str | None

    dataset_id: int

    model_type: str

    framework: str

    version: str

    mlflow_run_id: str | None

    artifact_uri: str

    metrics_json: dict[str, Any] | None

    status: ModelStatus

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )