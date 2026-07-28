from azure.storage.blob import BlobServiceClient

from app.config.settings import settings
from app.storage.base_storage import BaseStorage


class AzureBlobStorage(BaseStorage):
    """
    Azure Blob Storage implementation.
    """

    def __init__(self):
        account_url = (
            f"https://{settings.AZURE_STORAGE_ACCOUNT}.blob.core.windows.net"
        )

        self.client = BlobServiceClient(
            account_url=account_url,
            credential=settings.AZURE_STORAGE_KEY,
        )

        self.container = settings.AZURE_STORAGE_CONTAINER

    def upload_file(
        self,
        blob_path: str,
        data: bytes,
    ) -> str:

        blob_client = self.client.get_blob_client(
            container=self.container,
            blob=blob_path,
        )

        blob_client.upload_blob(
            data,
            overwrite=True,
        )

        return (
            f"https://"
            f"{settings.AZURE_STORAGE_ACCOUNT}"
            f".blob.core.windows.net/"
            f"{self.container}/"
            f"{blob_path}"
        )

    def delete_file(
        self,
        blob_path: str,
    ) -> None:

        blob_client = self.client.get_blob_client(
            container=self.container,
            blob=blob_path,
        )

        blob_client.delete_blob()

    def file_exists(
        self,
        blob_path: str,
    ) -> bool:

        blob_client = self.client.get_blob_client(
            container=self.container,
            blob=blob_path,
        )

        return blob_client.exists()

    def download_file(
        self,
        blob_path: str,
    ) -> bytes:

        blob_client = self.client.get_blob_client(
            container=self.container,
            blob=blob_path,
        )

        return blob_client.download_blob().readall()

    def list_files(
        self,
        folder: str,
    ) -> list[str]:

        container_client = self.client.get_container_client(
            self.container,
        )

        blobs = container_client.list_blobs(
            name_starts_with=folder,
        )

        return [
            blob.name
            for blob in blobs
        ]

    def download_files(
        self,
        folder: str,
    ) -> dict[str, bytes]:
        """
        Download every blob under a folder.
        """

        files: dict[str, bytes] = {}

        for blob_name in self.list_files(folder):
            files[blob_name] = self.download_file(blob_name)

        return files