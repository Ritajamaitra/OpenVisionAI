"""
Azure Blob Storage Provider

Responsibilities
----------------
- Upload files directly from bytes
- Download files directly as bytes
- Upload/download datasets, models and reports
- Delete blobs
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

    # =========================================================
    # Internal Helpers
    # =========================================================

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

    def _upload_bytes(
        self,
        container: str,
        blob_path: str,
        data: bytes,
        content_type: str | None = None,
    ) -> str:

        blob = self.client.get_blob_client(
            container=container,
            blob=blob_path,
        )

        upload_kwargs = {
            "overwrite": True,
        }

        if content_type:
            upload_kwargs["content_settings"] = {
                "content_type": content_type,
            }

        blob.upload_blob(
            data,
            **upload_kwargs,
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

    def _download_bytes(
        self,
        container: str,
        blob_path: str,
    ) -> bytes:

        blob = self.client.get_blob_client(
            container=container,
            blob=blob_path,
        )

        data = blob.download_blob()

        return data.readall()

    # =========================================================
    # Generic File API
    # =========================================================
    #
    # Used by:
    #   UploadService
    #   AutoAnnotationService
    #   Other application services
    #
    # =========================================================

    def upload_file(
        self,
        blob_path: str,
        data: bytes,
        content_type: str | None = None,
    ) -> str:

        return self._upload_bytes(
            container=settings.dataset_container,
            blob_path=blob_path,
            data=data,
            content_type=content_type,
        )

    def download_file(
        self,
        blob_path: str,
    ) -> bytes:

        return self._download_bytes(
            container=settings.dataset_container,
            blob_path=blob_path,
        )

    def delete_file(
        self,
        blob_path: str,
    ):

        self.delete_blob(
            container=settings.dataset_container,
            blob_path=blob_path,
        )

    # =========================================================
    # Dataset
    # =========================================================

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

    # =========================================================
    # Model
    # =========================================================

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

    # =========================================================
    # Report
    # =========================================================

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

    # =========================================================
    # Delete
    # =========================================================

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

    def download_files(
    self,
    blob_prefix: str,
) -> dict[str, bytes]:
        container_client = self.client.get_container_client(
        settings.dataset_container
    )
        files: dict[str, bytes] = {}

        prefix = blob_prefix.rstrip("/") + "/"

        for blob in container_client.list_blobs(
        name_starts_with=prefix
    ):
            blob_client = container_client.get_blob_client(
            blob.name
        )

            data = blob_client.download_blob().readall()

            relative_path = blob.name[len(prefix):]

            if relative_path:
                files[relative_path] = data

        return files