"""
OpenVisionAI Azure Deployment Client

Responsibilities
----------------
1. Create Managed Online Endpoints
2. Deploy registered models
3. Retrieve endpoints
4. List endpoints
5. Delete endpoints
"""

from azure.ai.ml.entities import (
    ManagedOnlineDeployment,
    ManagedOnlineEndpoint,
)
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
)

from app.integrations.azureml.client import get_azure_ml_client
from app.integrations.azureml.contracts import (
    AzureDeployment,
    AzureEndpoint,
    DeploymentRequest,
)
from app.integrations.azureml.exceptions import (
    DeploymentException,
    EndpointNotFoundException,
)


class AzureDeploymentClient:

    def __init__(self):

        self.client = get_azure_ml_client().client

    # ==========================================================
    # Create Endpoint
    # ==========================================================

    def create_endpoint(
        self,
        endpoint_name: str,
        description: str | None = None,
        auth_mode: str = "key",
    ) -> AzureEndpoint:

        try:

            endpoint = ManagedOnlineEndpoint(
                name=endpoint_name,
                description=description,
                auth_mode=auth_mode,
            )

            endpoint = (
                self.client.online_endpoints
                .begin_create_or_update(endpoint)
                .result()
            )

            return AzureEndpoint(
                name=endpoint.name,
                scoring_uri=endpoint.scoring_uri,
                provisioning_state=endpoint.provisioning_state,
            )

        except HttpResponseError as ex:

            raise DeploymentException(
                str(ex)
            ) from ex

    # ==========================================================
    # Deploy Model
    # ==========================================================

    def deploy_model(
        self,
        request: DeploymentRequest,
    ) -> AzureDeployment:

        try:

            deployment = ManagedOnlineDeployment(
                name=request.deployment_name,
                endpoint_name=request.endpoint_name,
                model=f"{request.model_name}:{request.model_version}",
                instance_type=request.instance_type,
                instance_count=request.instance_count,
            )

            deployment = (
                self.client.online_deployments
                .begin_create_or_update(deployment)
                .result()
            )

            return AzureDeployment(
                endpoint_name=deployment.endpoint_name,
                deployment_name=deployment.name,
                model_name=request.model_name,
                model_version=request.model_version,
                provisioning_state=deployment.provisioning_state,
            )

        except HttpResponseError as ex:

            raise DeploymentException(
                str(ex)
            ) from ex

    # ==========================================================
    # Get Endpoint
    # ==========================================================

    def get_endpoint(
        self,
        endpoint_name: str,
    ) -> AzureEndpoint:

        try:

            endpoint = self.client.online_endpoints.get(
                endpoint_name
            )

            return AzureEndpoint(
                name=endpoint.name,
                scoring_uri=endpoint.scoring_uri,
                provisioning_state=endpoint.provisioning_state,
            )

        except ResourceNotFoundError as ex:

            raise EndpointNotFoundException(
                f"Endpoint '{endpoint_name}' not found."
            ) from ex

    # ==========================================================
    # List Endpoints
    # ==========================================================

    def list_endpoints(
        self,
    ) -> list[AzureEndpoint]:

        endpoints = []

        for endpoint in self.client.online_endpoints.list():

            endpoints.append(

                AzureEndpoint(
                    name=endpoint.name,
                    scoring_uri=endpoint.scoring_uri,
                    provisioning_state=endpoint.provisioning_state,
                )

            )

        return endpoints

    # ==========================================================
    # Delete Endpoint
    # ==========================================================

    def delete_endpoint(
        self,
        endpoint_name: str,
    ) -> None:

        try:

            self.client.online_endpoints.begin_delete(
                endpoint_name
            ).result()

        except HttpResponseError as ex:

            raise DeploymentException(
                str(ex)
            ) from ex