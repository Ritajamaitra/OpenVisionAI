from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.report_status import ReportStatus


class ReportCreate(BaseModel):
    """
    Request schema for creating a report.
    """

    name: str = Field(
        min_length=3,
        max_length=255,
    )

    report_type: str = Field(
        min_length=2,
        max_length=100,
    )

    report_uri: str = Field(
        min_length=1,
        max_length=1024,
    )

    model_registry_id: int


class ReportUpdate(BaseModel):
    """
    Request schema for updating report metadata.
    """

    name: str | None = Field(
        default=None,
        min_length=3,
        max_length=255,
    )

    report_type: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    report_uri: str | None = Field(
        default=None,
        min_length=1,
        max_length=1024,
    )

    status: ReportStatus | None = None


class ReportResponse(BaseModel):
    """
    Response schema returned to API clients.
    """

    id: int

    name: str

    project_id: int

    model_registry_id: int

    report_type: str

    report_uri: str

    generated_at: datetime

    status: ReportStatus

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )