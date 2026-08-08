"""
Abstract Storage Provider
"""

from abc import ABC, abstractmethod


class BaseStorage(ABC):

    @abstractmethod
    def upload_dataset(
        self,
        local_file: str,
        blob_path: str,
    ) -> str:
        pass

    @abstractmethod
    def download_dataset(
        self,
        blob_path: str,
        local_file: str,
    ) -> None:
        pass

    @abstractmethod
    def upload_model(
        self,
        local_file: str,
        blob_path: str,
    ) -> str:
        pass

    @abstractmethod
    def download_model(
        self,
        blob_path: str,
        local_file: str,
    ) -> None:
        pass

    @abstractmethod
    def upload_report(
        self,
        local_file: str,
        blob_path: str,
    ) -> str:
        pass

    @abstractmethod
    def delete_blob(
        self,
        container: str,
        blob_path: str,
    ) -> None:
        pass