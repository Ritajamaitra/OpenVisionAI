"""
Azure Blob Storage Provider

10.4 additions:
- list_dataset_images()
- download_dataset_image()
- upload_file() for direct byte uploads
"""

from pathlib import Path

from azure.storage.blob import BlobServiceClient
from azure.storage.blob import ContentSettings

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

    # =========================================================
    # Generic Byte Upload
    # =========================================================

    def upload_file(
        self,
        blob_path: str,
        data: bytes,
        content_type: str | None = None,
    ) -> str:
        """
        Upload raw bytes directly to the dataset container.

        Used by:
        - Dataset image uploads
        - Annotation uploads
        - Auto-generated annotation files
        """

        blob = self.client.get_blob_client(
            container=settings.dataset_container,
            blob=blob_path,
        )

        upload_kwargs = {
            "overwrite": True,
        }

        if content_type:
            upload_kwargs["content_settings"] = ContentSettings(
                content_type=content_type
            )

        blob.upload_blob(
            data,
            **upload_kwargs,
        )

        return blob.url

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
    # Dataset Image Browser / Viewer
    # =========================================================

    def list_dataset_images(
        self,
        image_prefix: str,
    ) -> list[str]:
        """
        Return image filenames under a dataset image prefix.
        """

        container = self.client.get_container_client(
            settings.dataset_container
        )

        allowed_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
            ".bmp",
            ".gif",
        }

        image_names: list[str] = []

        for blob in container.list_blobs(
            name_starts_with=image_prefix
        ):

            blob_name = blob.name

            filename = Path(
                blob_name
            ).name

            if (
                Path(filename).suffix.lower()
                in allowed_extensions
            ):
                image_names.append(
                    filename
                )

        return sorted(
            set(image_names),
            key=str.lower,
        )

    def download_dataset_image(
        self,
        blob_path: str,
    ) -> tuple[bytes, str]:
        """
        Download an image and return:

        (
            image_bytes,
            content_type
        )
        """

        blob = self.client.get_blob_client(
            container=settings.dataset_container,
            blob=blob_path,
        )

        properties = (
            blob.get_blob_properties()
        )

        content_type = (
            properties
            .content_settings
            .content_type
        )

        if not content_type:

            suffix = (
                Path(blob_path)
                .suffix
                .lower()
            )

            content_type = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".webp": "image/webp",
                ".bmp": "image/bmp",
                ".gif": "image/gif",
            }.get(
                suffix,
                "application/octet-stream",
            )

        return (
            blob
            .download_blob()
            .readall(),
            content_type,
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