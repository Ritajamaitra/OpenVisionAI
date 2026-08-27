from datetime import datetime
from pydantic import BaseModel, Field


class DeploymentCreate(BaseModel):
    endpoint_name: str | None = Field(
        default=None,
        min_length=3,
        max_length=100,
    )
    deployment_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    instance_type: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    instance_count: int | None = Field(
        default=None,
        ge=1,
        le=10,
    )


class DeploymentResponse(BaseModel):
    model_id: int
    model_name: str
    model_version: str
    dataset_name: str | None
    endpoint_name: str
    deployment_name: str
    deployment_status: str
    endpoint_status: str
    endpoint_url: str | None
    instance_type: str | None
    instance_count: int | None
    azure_model_reference: str
    created_at: datetime | None = None


class EndpointResponse(BaseModel):
    endpoint_name: str
    endpoint_status: str
    endpoint_url: str | None
