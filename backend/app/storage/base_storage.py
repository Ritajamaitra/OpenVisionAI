from abc import ABC, abstractmethod


class BaseStorage(ABC):
    """
    Abstract storage interface.

    Allows OpenVisionAI to switch between:

    Azure Blob

    AWS S3

    GCS

    ADLS

    without changing the UploadService.
    """

    @abstractmethod
    def upload_file(
        self,
        blob_path: str,
        data: bytes,
    ) -> str:
        """
        Upload a file to the given blob path.

        Returns the storage URI.
        """
        pass

    @abstractmethod
    def delete_file(
        self,
        blob_path: str,
    ) -> None:
        """
        Delete a stored file.
        """
        pass

    @abstractmethod
    def file_exists(
        self,
        blob_path: str,
    ) -> bool:
        """
        Check whether a blob exists.
        """
        pass

    @abstractmethod
    def download_file(
        self,
        blob_path: str,
    ) -> bytes:
        """
        Download a blob.
        """
        pass