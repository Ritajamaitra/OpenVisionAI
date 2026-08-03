"""
OpenVisionAI Azure ML Client

Creates and exposes a single authenticated MLClient
for the Azure integration layer.
"""

from functools import lru_cache

from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

from app.config.settings import settings


class AzureMLClient:
    """
    Factory for authenticated Azure ML SDK clients.
    """

    def __init__(self):

        self._credential = DefaultAzureCredential()

        self._client = MLClient(
            credential=self._credential,
            subscription_id=settings.azure_subscription_id,
            resource_group_name=settings.azure_resource_group,
            workspace_name=settings.azure_ml_workspace,
        )

    @property
    def credential(self):
        return self._credential

    @property
    def client(self) -> MLClient:
        return self._client


@lru_cache(maxsize=1)
def get_azure_ml_client() -> AzureMLClient:
    """
    Returns a cached AzureMLClient instance.
    """

    return AzureMLClient()