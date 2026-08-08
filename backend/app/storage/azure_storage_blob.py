"""
Azure Blob Storage Provider
"""

from pathlib import Path

from azure.storage.blob import BlobServiceClient

from app.config.settings import settings
from app.storage.base_storage import BaseStorage


class AzureBlobStorage(BaseStorage):

    def __init__(self):

        self.client = BlobServiceClient.from_connection_string(
            settings.storage_connection_string
        )

    # ---------------------------------------------------------
    # Internal Helpers
    # ---------------------------------------------------------

    def _upload(
        self,
        container: str,
        local_file: str,
        blob_path: str,
    ) -> str:

        blob = self.client.get_blob_client(
            container=container,
            blob=blob_path,
        )

        with open(local_file, "rb") as f:

            blob.upload_blob(
                f,
                overwrite=True,
            )

        return blob.url

    def _download(
        self,
        container: str,
        blob_path: str,
        local_file: str,
    ):

        blob = self.client.get_blob_client(
            container=container,
            blob=blob_path,
        )

        Path(local_file).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(local_file, "wb") as f:

            data = blob.download_blob()

            f.write(data.readall())

    # ---------------------------------------------------------
    # Dataset
    # ---------------------------------------------------------

    def upload_dataset(
        self,
        local_file: str,
        blob_path: str,
    ) -> str:

        return self._upload(
            settings.dataset_container,
            local_file,
            blob_path,
        )

    def download_dataset(
        self,
        blob_path: str,
        local_file: str,
    ):

        self._download(
            settings.dataset_container,
            blob_path,
            local_file,
        )

    # ---------------------------------------------------------
    # Model
    # ---------------------------------------------------------

    def upload_model(
        self,
        local_file: str,
        blob_path: str,
    ) -> str:

        return self._upload(
            settings.model_container,
            local_file,
            blob_path,
        )

    def download_model(
        self,
        blob_path: str,
        local_file: str,
    ):

        self._download(
            settings.model_container,
            blob_path,
            local_file,
        )

    # ---------------------------------------------------------
    # Report
    # ---------------------------------------------------------

    def upload_report(
        self,
        local_file: str,
        blob_path: str,
    ) -> str:

        return self._upload(
            settings.report_container,
            local_file,
            blob_path,
        )

    # ---------------------------------------------------------
    # Delete
    # ---------------------------------------------------------

    def delete_blob(
        self,
        container: str,
        blob_path: str,
    ):

        blob = self.client.get_blob_client(
            container=container,
            blob=blob_path,
        )

        blob.delete_blob()