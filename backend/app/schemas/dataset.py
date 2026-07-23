from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.dataset_status import DatasetStatus

class DatasetCreate(BaseModel):
    """
    Request schema for creating a dataset.
    """

    name: str = Field(
        min_length=3,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    storage_path: str = Field(
        min_length=1,
        max_length=2048,
    )

    dataset_version: str = Field(
        min_length=1,
        max_length=50,
    )


class DatasetUpdate(BaseModel):
    """
    Request schema for updating a dataset.
    Only supplied fields will be updated.
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

    storage_path: str | None = Field(
        default=None,
        min_length=1,
        max_length=2048,
    )

    dataset_version: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )


class DatasetResponse(BaseModel):
    """
    Response schema returned to API clients.
    """

    id: int

    name: str
    description: str | None

    project_id: int

    storage_path: str
    dataset_version: str

    total_images: int
    total_annotations: int

    status: DatasetStatus

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )