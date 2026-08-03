"""
OpenVisionAI Azure ML Models

Internal data models returned by the Azure integration layer.

These classes isolate the rest of the application from the
Azure SDK object model.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


# ==========================================================
# Workspace
# ==========================================================

@dataclass(slots=True)
class AzureWorkspace:

    name: str
    location: str
    resource_group: str
    subscription_id: str


# ==========================================================
# Environment
# ==========================================================

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
# ==========================================================
# Training Job
# ==========================================================

@dataclass(slots=True)
class AzureJob:

    name: str
    display_name: str
    status: str
    experiment_name: str

    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# ==========================================================
# Training Metrics
# ==========================================================

@dataclass(slots=True)
class AzureJobMetrics:

    precision: float = 0.0
    recall: float = 0.0
    map50: float = 0.0
    map50_95: float = 0.0
    training_time: float = 0.0


# ==========================================================
# Registered Model
# ==========================================================

@dataclass(slots=True)
class AzureModel:

    name: str
    version: str

    description: Optional[str] = None

    created_at: Optional[datetime] = None


# ==========================================================
# Managed Endpoint
# ==========================================================

@dataclass(slots=True)
class AzureEndpoint:

    name: str

    scoring_uri: str

    provisioning_state: str


# ==========================================================
# Deployment
# ==========================================================

@dataclass(slots=True)
class AzureDeployment:

    endpoint_name: str

    deployment_name: str

    model_name: str

    model_version: str

    provisioning_state: str


# ==========================================================
# Datastore
# ==========================================================

@dataclass(slots=True)
class AzureDatastore:

    name: str

    account_name: str

    container_name: str