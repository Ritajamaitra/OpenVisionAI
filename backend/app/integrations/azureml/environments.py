"""
OpenVisionAI Azure Environment Client

Responsibilities
----------------
1. Register Azure ML environments
2. Retrieve environments
3. List environments
4. Archive environments
"""

from azure.ai.ml.entities import Environment
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
)

from app.integrations.azureml.client import get_azure_ml_client
from app.integrations.azureml.contracts import (
    AzureEnvironment,
    EnvironmentRegistrationRequest,
)
from app.integrations.azureml.exceptions import (
    EnvironmentNotFoundException,
    EnvironmentRegistrationException,
)


class AzureEnvironmentClient:

    def __init__(self):

        self.client = get_azure_ml_client().client

    # ==========================================================
    # Register Environment
    # ==========================================================

    def register_environment(
        self,
        request: EnvironmentRegistrationRequest,
    ) -> AzureEnvironment:

        try:

            environment = Environment(
                name=request.name,
                version=request.version,
                build=dict(
                    path=request.build_path,
                ),
            )

            environment = (
                self.client.environments
                .create_or_update(environment)
            )

            return AzureEnvironment(
                name=environment.name,
                version=str(environment.version),
                description=environment.description,
            )

        except HttpResponseError as ex:

            raise EnvironmentRegistrationException(
                str(ex)
            ) from ex

    # ==========================================================
    # Get Environment
    # ==========================================================

    def get_environment(
        self,
        name: str,
        version: str,
    ) -> AzureEnvironment:

        try:

            environment = self.client.environments.get(
                name=name,
                version=version,
            )

            return AzureEnvironment(
                name=environment.name,
                version=str(environment.version),
                description=environment.description,
            )

        except ResourceNotFoundError as ex:

            raise EnvironmentNotFoundException(
                f"Environment '{name}:{version}' not found."
            ) from ex

    # ==========================================================
    # List Environments
    # ==========================================================

    def list_environments(
        self,
    ) -> list[AzureEnvironment]:

        environments = []

        for env in self.client.environments.list():

            environments.append(

                AzureEnvironment(
                    name=env.name,
                    version=str(env.version),
                    description=env.description,
                )

            )

        return environments

    # ==========================================================
    # Archive Environment
    # ==========================================================

    def archive_environment(
        self,
        name: str,
        version: str,
    ) -> None:

        try:

            self.client.environments.archive(
                name=name,
                version=version,
            )

        except HttpResponseError as ex:

            raise EnvironmentRegistrationException(
                str(ex)
            ) from ex