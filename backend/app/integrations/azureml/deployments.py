"""
OpenVisionAI Azure ML Deployment Client

Responsibilities
----------------
1. Create managed online endpoints
2. Deploy registered YOLO models
3. Retrieve endpoints
4. List endpoints
5. Delete endpoints

All Azure ML SDK-specific logic stays here.
"""

from azure.ai.ml.entities import (
    CodeConfiguration,
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
                .begin_create_or_update(
                    endpoint
                )
                .result()
            )

            return AzureEndpoint(
                name=endpoint.name,
                scoring_uri=endpoint.scoring_uri,
                provisioning_state=(
                    endpoint.provisioning_state
                ),
            )

        except HttpResponseError as exc:

            raise DeploymentException(
                f"Failed to create endpoint "
                f"'{endpoint_name}': {exc}"
            ) from exc

    # ==========================================================
    # Deploy Registered Model
    # ==========================================================

    def deploy_model(
        self,
        request: DeploymentRequest,
        environment_name: str,
        environment_version: str,
        scoring_code_path: str,
        scoring_script: str = "score.py",
    ) -> AzureDeployment:

        try:

            model_reference = (
                f"azureml:"
                f"{request.model_name}:"
                f"{request.model_version}"
            )

            environment_reference = (
                f"azureml:"
                f"{environment_name}:"
                f"{environment_version}"
            )

            deployment = ManagedOnlineDeployment(
                name=request.deployment_name,

                endpoint_name=request.endpoint_name,

                model=model_reference,

                environment=environment_reference,

                code_configuration=CodeConfiguration(
                    code=scoring_code_path,
                    scoring_script=scoring_script,
                ),

                instance_type=request.instance_type,

                instance_count=request.instance_count,
            )

            deployment = (
                self.client.online_deployments
                .begin_create_or_update(
                    deployment
                )
                .result()
            )

            return AzureDeployment(
                endpoint_name=(
                    deployment.endpoint_name
                ),

                deployment_name=(
                    deployment.name
                ),

                model_name=request.model_name,

                model_version=(
                    request.model_version
                ),

                provisioning_state=(
                    deployment.provisioning_state
                ),
            )

        except HttpResponseError as exc:

            raise DeploymentException(
                f"Failed to deploy "
                f"'{request.model_name}:"
                f"{request.model_version}': {exc}"
            ) from exc

    # ==========================================================
    # Get Endpoint
    # ==========================================================

    def get_endpoint(
        self,
        endpoint_name: str,
    ) -> AzureEndpoint:

        try:

            endpoint = (
                self.client.online_endpoints.get(
                    endpoint_name
                )
            )

            return AzureEndpoint(
                name=endpoint.name,

                scoring_uri=(
                    endpoint.scoring_uri
                ),

                provisioning_state=(
                    endpoint.provisioning_state
                ),
            )

        except ResourceNotFoundError as exc:

            raise EndpointNotFoundException(
                f"Endpoint '{endpoint_name}' "
                f"not found."
            ) from exc

    # ==========================================================
    # List Endpoints
    # ==========================================================

    def list_endpoints(
        self,
    ) -> list[AzureEndpoint]:

        endpoints = []

        for endpoint in (
            self.client.online_endpoints.list()
        ):

            endpoints.append(
                AzureEndpoint(
                    name=endpoint.name,

                    scoring_uri=(
                        endpoint.scoring_uri
                    ),

                    provisioning_state=(
                        endpoint.provisioning_state
                    ),
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

            (
                self.client
                .online_endpoints
                .begin_delete(
                    endpoint_name
                )
                .result()
            )

        except HttpResponseError as exc:

            raise DeploymentException(
                f"Failed to delete endpoint "
                f"'{endpoint_name}': {exc}"
            ) from exc

    # ==========================================================
    # Invoke Endpoint
    # ==========================================================

    def invoke_endpoint(
        self,
        endpoint_name: str,
        deployment_name: str,
        request_file: str,
    ):

        try:

            return (
                self.client
                .online_endpoints
                .invoke(
                    endpoint_name=endpoint_name,
                    deployment_name=deployment_name,
                    request_file=request_file,
                )
            )

        except HttpResponseError as exc:

            raise DeploymentException(
                f"Endpoint invocation failed: {exc}"
            ) from exc