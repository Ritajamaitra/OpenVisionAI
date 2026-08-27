"""
OpenVisionAI Azure ML Deployment Client.

Azure SDK-specific logic for managed online endpoints and deployments.
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

        except HttpResponseError as exc:
            raise DeploymentException(
                f"Failed to create endpoint '{endpoint_name}': {exc}"
            ) from exc

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
                f"azureml:{request.model_name}:{request.model_version}"
            )

            environment_reference = (
                f"azureml:{environment_name}:{environment_version}"
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
                .begin_create_or_update(deployment)
                .result()
            )

            return AzureDeployment(
                endpoint_name=deployment.endpoint_name,
                deployment_name=deployment.name,
                model_name=request.model_name,
                model_version=request.model_version,
                provisioning_state=deployment.provisioning_state,
                instance_type=getattr(
                    deployment,
                    "instance_type",
                    request.instance_type,
                ),
                instance_count=getattr(
                    deployment,
                    "instance_count",
                    request.instance_count,
            ),
            )

        except HttpResponseError as exc:
            raise DeploymentException(
                f"Failed to deploy "
                f"'{request.model_name}:{request.model_version}': {exc}"
            ) from exc

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

        except ResourceNotFoundError as exc:
            raise EndpointNotFoundException(
                f"Endpoint '{endpoint_name}' not found."
            ) from exc

    def list_endpoints(self) -> list[AzureEndpoint]:
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

    def list_deployments(
        self,
        endpoint_name: str,
    ) -> list[AzureDeployment]:
        """
        Return all managed deployments for an endpoint.

        This is used by the OpenVisionAI Deployment Management UI to
        display the deployed model, version, runtime status and compute.
        """
        deployments = []

        for deployment in self.client.online_deployments.list(
            endpoint_name=endpoint_name
        ):
            model = getattr(deployment, "model", None)
            model_name = ""
            model_version = ""

            if model:
                model_reference = str(model)
                if model_reference.startswith("azureml:"):
                    model_reference = model_reference[len("azureml:"):]

                parts = model_reference.rsplit(":", 1)
                if len(parts) == 2:
                    model_name, model_version = parts

            deployments.append(
                AzureDeployment(
                    endpoint_name=deployment.endpoint_name,
                    deployment_name=deployment.name,
                    model_name=model_name,
                    model_version=model_version,
                    provisioning_state=getattr(
                        deployment,
                        "provisioning_state",
                        "Unknown",
                    ),
                    instance_type=getattr(
                        deployment,
                        "instance_type",
                        None,
                    ),
                    instance_count=getattr(
                        deployment,
                        "instance_count",
                        None,
                    ),
                )
            )

        return deployments

    def delete_endpoint(
        self,
        endpoint_name: str,
    ) -> None:
        try:
            (
                self.client
                .online_endpoints
                .begin_delete(endpoint_name)
                .result()
            )
        except HttpResponseError as exc:
            raise DeploymentException(
                f"Failed to stop endpoint '{endpoint_name}': {exc}"
            ) from exc

    def invoke_endpoint(
        self,
        endpoint_name: str,
        deployment_name: str,
        request_file: str,
    ):
        try:
            return self.client.online_endpoints.invoke(
                endpoint_name=endpoint_name,
                deployment_name=deployment_name,
                request_file=request_file,
            )
        except HttpResponseError as exc:
            raise DeploymentException(
                f"Endpoint invocation failed: {exc}"
            ) from exc
