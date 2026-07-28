from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.upload import (
    DatasetPreviewResponse,
    UploadAnnotationResponse,
    UploadImageResponse,
)
from app.services.dataset_services import DatasetService
from app.storage.azure_storage_blob import AzureBlobStorage
from app.utils.file_validation import (
    validate_annotation_file,
    validate_file_size,
    validate_image_file,
)


class UploadService:
    """
    Handles dataset uploads.

    Responsibilities:
    - Validate uploads
    - Upload files to Azure Blob Storage
    - Update dataset statistics
    """

    def __init__(self):
        self.dataset_service = DatasetService()
        self.storage = AzureBlobStorage()

    # -----------------------------------------------------
    # Image Upload
    # -----------------------------------------------------

    async def upload_image(
        self,
        db: Session,
        dataset_id: int,
        file: UploadFile,
        current_user: User,
    ) -> UploadImageResponse:

        validate_image_file(file)

        dataset = self.dataset_service.get_dataset(
            db=db,
            dataset_id=dataset_id,
            current_user=current_user,
        )

        contents = await file.read()

        validate_file_size(len(contents))

        folder = (
            f"datasets/"
            f"project_{dataset.project_id}/"
            f"dataset_{dataset.id}/"
            f"images"
        )

        blob_path = f"{folder}/{file.filename}"

        storage_path = self.storage.upload_file(
            blob_path=blob_path,
            data=contents,
        )

        # -----------------------------
        # Update Dataset Statistics
        # -----------------------------

        dataset.total_images += 1

        self.dataset_service.update_statistics(
            db=db,
            dataset=dataset,
        )

        return UploadImageResponse(
            filename=file.filename,
            storage_path=storage_path,
            image_size=len(contents),
            content_type=file.content_type,
        )

    # -----------------------------------------------------
    # Annotation Upload
    # -----------------------------------------------------

    async def upload_annotation(
        self,
        db: Session,
        dataset_id: int,
        file: UploadFile,
        current_user: User,
    ) -> UploadAnnotationResponse:

        validate_annotation_file(file)

        dataset = self.dataset_service.get_dataset(
            db=db,
            dataset_id=dataset_id,
            current_user=current_user,
        )

        contents = await file.read()

        validate_file_size(len(contents))

        extension = Path(file.filename).suffix.lower()

        annotation_format = {
            ".json": "COCO",
            ".xml": "Pascal VOC",
            ".txt": "YOLO",
        }.get(extension, "Unknown")

        folder = (
            f"datasets/"
            f"project_{dataset.project_id}/"
            f"dataset_{dataset.id}/"
            f"annotations"
        )

        blob_path = f"{folder}/{file.filename}"

        storage_path = self.storage.upload_file(
            blob_path=blob_path,
            data=contents,
        )

        # -----------------------------
        # Update Dataset Statistics
        # -----------------------------

        dataset.annotated_images += 1

        dataset.total_annotations += 1

        self.dataset_service.update_statistics(
            db=db,
            dataset=dataset,
        )

        return UploadAnnotationResponse(
            filename=file.filename,
            storage_path=storage_path,
            annotation_format=annotation_format,
        )

    # -----------------------------------------------------
    # Dataset Preview
    # -----------------------------------------------------

    def preview_dataset(
        self,
        db: Session,
        dataset_id: int,
        current_user: User,
    ) -> DatasetPreviewResponse:

        dataset = self.dataset_service.get_dataset(
            db=db,
            dataset_id=dataset_id,
            current_user=current_user,
        )

        return DatasetPreviewResponse(
            dataset_id=dataset.id,
            total_images=dataset.total_images,
            total_annotations=dataset.total_annotations,
            storage_path=dataset.storage_path,
            dataset_version=dataset.dataset_version,
        )