from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.project_status import ProjectStatus


class ProjectCreate(BaseModel):
    """
    Request schema for creating a new project.
    """

    name: str = Field(
        min_length=3,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )


class ProjectUpdate(BaseModel):
    """
    Request schema for updating an existing project.
    All fields are optional.
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


class ProjectResponse(BaseModel):
    """
    Response schema returned by the API.
    """

    id: int

    name: str

    description: str | None

    status: ProjectStatus

    owner_id: int

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )