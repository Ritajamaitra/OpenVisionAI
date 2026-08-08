"""
OpenVisionAI Azure ML Facade

Responsibilities
----------------
Provides a single entry point to all Azure ML integration clients.

This module contains no business logic.
It simply composes the Azure integration layer.
"""

from functools import cached_property

from app.integrations.azureml.jobs import (
    AzureJobsClient,
)
from app.integrations.azureml.monitoring import (
    AzureMonitoringClient,
)
from app.integrations.azureml.registry import (
    AzureRegistryClient,
)
from app.integrations.azureml.deployments import (
    AzureDeploymentClient,
)
from app.integrations.azureml.environments import (
    AzureEnvironmentClient,
)
from app.integrations.azureml.datastores import (
    AzureDatastoreClient,
)


class AzureML:
    """
    Facade for the OpenVisionAI Azure ML SDK.

    Example
    -------
    azure = AzureML()

    job = azure.jobs.submit_training_job(...)
    status = azure.monitoring.get_status(job.name)
    model = azure.registry.register_job_output(...)
    endpoint = azure.deployments.create_endpoint(...)
    """

    @cached_property
    def jobs(self) -> AzureJobsClient:
        return AzureJobsClient()

    @cached_property
    def monitoring(self) -> AzureMonitoringClient:
        return AzureMonitoringClient()

    @cached_property
    def registry(self) -> AzureRegistryClient:
        return AzureRegistryClient()

    @cached_property
    def deployments(self) -> AzureDeploymentClient:
        return AzureDeploymentClient()

    @cached_property
    def environments(self) -> AzureEnvironmentClient:
        return AzureEnvironmentClient()

    @cached_property
    def datastores(self) -> AzureDatastoreClient:
        return AzureDatastoreClient()


azure_ml = AzureML()