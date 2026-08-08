"""
OpenVisionAI Azure ML Datastore Client

Responsibilities
----------------
1. Retrieve Azure ML datastores
2. List available datastores
3. Validate datastore existence
4. Build AzureML datastore URIs

This module does NOT upload files.
Uploads are handled by AzureBlobStorage.
"""

from azure.core.exceptions import (
    ResourceNotFoundError,
)

from app.config.settings import settings

from app.integrations.azureml.client import (
    get_azure_ml_client,
)

from app.integrations.azureml.contracts import (
    AzureDatastore,
)

from app.integrations.azureml.exceptions import (
    DatastoreNotFoundException,
)


class AzureDatastoreClient:

    def __init__(self):

        self.client = get_azure_ml_client().client

    # ==========================================================
    # Helpers
    # ==========================================================

    @staticmethod
    def _to_contract(datastore) -> AzureDatastore:

        return AzureDatastore(

            name=datastore.name,

            datastore_type=type(datastore).__name__,

            account_name=getattr(
                datastore,
                "account_name",
                None,
            ),

            path_name=(

                getattr(
                    datastore,
                    "container_name",
                    None,
                )

                or getattr(
                    datastore,
                    "file_share_name",
                    None,
                )

                or getattr(
                    datastore,
                    "filesystem",
                    None,
                )

            ),

        )

    # ==========================================================
    # Get Datastore
    # ==========================================================

    def get_datastore(
        self,
        datastore_name: str,
    ) -> AzureDatastore:

        try:

            datastore = self.client.datastores.get(
                datastore_name,
            )

            return self._to_contract(datastore)

        except ResourceNotFoundError as ex:

            raise DatastoreNotFoundException(
                f"Datastore '{datastore_name}' not found."
            ) from ex

    # ==========================================================
    # List Datastores
    # ==========================================================

    def list_datastores(
        self,
    ) -> list[AzureDatastore]:

        return [

            self._to_contract(datastore)

            for datastore in self.client.datastores.list()

        ]

    # ==========================================================
    # Exists
    # ==========================================================

    def datastore_exists(
        self,
        datastore_name: str,
    ) -> bool:

        try:

            self.client.datastores.get(
                datastore_name,
            )

            return True

        except ResourceNotFoundError:

            return False

    # ==========================================================
    # AzureML URI
    # ==========================================================

    def build_uri(
        self,
        relative_path: str,
        datastore_name: str | None = None,
    ) -> str:
        """
        Example

        azureml://datastores/datasets/paths/project_1/images.zip
        """

        datastore = (
            datastore_name
            or settings.dataset_container
        )

        relative_path = relative_path.lstrip("/")

        return (

            f"azureml://datastores/"
            f"{datastore}/paths/"
            f"{relative_path}"

        )