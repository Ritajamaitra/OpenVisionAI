"""
OpenVisionAI Azure ML Models

Internal data models returned by the Azure integration layer.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class AzureWorkspace:
    name: str
    location: str
    resource_group: str
    subscription_id: str


@dataclass(slots=True)
class AzureEnvironment:
    name: str
    version: str
    description: Optional[str] = None


@dataclass(slots=True)
class TrainingJobRequest:
    experiment_name: str
    display_name: str
    dataset_uri: str
    model_name: str
    epochs: int
    imgsz: int
    batch: int
    compute: str
    environment: str


@dataclass(slots=True)
class ModelRegistrationRequest:
    model_name: str
    model_path: str
    description: str | None = None


@dataclass(slots=True)
class DeploymentRequest:
    endpoint_name: str
    deployment_name: str
    model_name: str
    model_version: str
    instance_type: str
    instance_count: int = 1


@dataclass(slots=True)
class EnvironmentRegistrationRequest:
    name: str
    version: str
    build_path: str


@dataclass(slots=True)
class AzureJob:
    name: str
    display_name: str
    status: str
    experiment_name: str
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass(slots=True)
class AzureJobMetrics:
    precision: float = 0.0
    recall: float = 0.0
    map50: float = 0.0
    map50_95: float = 0.0
    training_time: float = 0.0


@dataclass(slots=True)
class AzureModel:
    name: str
    version: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass(slots=True)
class AzureEndpoint:
    name: str
    scoring_uri: str
    provisioning_state: str


@dataclass(slots=True)
class AzureDeployment:
    endpoint_name: str
    deployment_name: str
    model_name: str
    model_version: str
    provisioning_state: str
    instance_type: str | None = None
    instance_count: int | None = None


@dataclass(slots=True)
class AzureDatastore:
    name: str
    datastore_type: str
    account_name: str | None = None
    path_name: str | None = None
