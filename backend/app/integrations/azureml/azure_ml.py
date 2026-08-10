"""
OpenVisionAI Azure ML Facade

Responsibilities
----------------
Provides a single entry point to the Azure ML integration layer.

This module contains no business logic. It composes the Azure-specific
clients and exposes the authenticated MLClient only for components that
still require direct Azure ML SDK access.
"""

from functools import cached_property

from azure.ai.ml import MLClient

from app.integrations.azureml.client import get_azure_ml_client
from app.integrations.azureml.jobs import AzureJobsClient
from app.integrations.azureml.monitoring import AzureMonitoringClient
from app.integrations.azureml.registry import AzureRegistryClient
from app.integrations.azureml.deployments import AzureDeploymentClient
from app.integrations.azureml.environments import AzureEnvironmentClient
from app.integrations.azureml.datastores import AzureDatastoreClient


class AzureML:
    """
    Facade for the OpenVisionAI Azure ML integration layer.

    Preferred usage:

        azure_ml.jobs
        azure_ml.monitoring
        azure_ml.registry
        azure_ml.deployments
        azure_ml.environments
        azure_ml.datastores

    `azure_ml.client` is exposed only for application components that
    still require the raw Azure ML SDK client.
    """

    @cached_property
    def client(self) -> MLClient:
        """
        Return the authenticated Azure ML SDK client.

        Authentication and workspace configuration remain centralized
        in app.integrations.azureml.client.
        """
        return get_azure_ml_client().client

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


def get_ml_client() -> MLClient:
    """
    Backward-compatible accessor for existing application code.

    New code should prefer:
        azure_ml.client
    """
    return azure_ml.client