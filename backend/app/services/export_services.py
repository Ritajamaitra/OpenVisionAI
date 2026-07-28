from app.ai.exporters.coco_exporter import COCOExporter
from app.ai.exporters.voc_exporter import VOCExporter
from app.ai.exporters.yolo_exporter import YOLOExporter
from app.ai.exporters.zip_exporter import ZipExporter

from app.repositories.annotation_repository import AnnotationRepository
from app.schemas.export import (
    DatasetExportResponse,
    ExportFormat,
)
from app.services.dataset_services import DatasetService
from app.storage.azure_storage_blob import AzureBlobStorage
import inspect


class ExportService:
    """
    Export datasets into YOLO, COCO or Pascal VOC.
    """

    def __init__(self):

        self.dataset_service = DatasetService()

        self.annotation_repository = AnnotationRepository()

        self.storage = AzureBlobStorage()
        print("Storage class:", type(self.storage))
        print("Loaded from:", inspect.getfile(AzureBlobStorage))
        print("Has download_files:", hasattr(self.storage, "download_files"))

        self.yolo = YOLOExporter()

        self.coco = COCOExporter()

        self.voc = VOCExporter()

        self.zipper = ZipExporter()

    def export_dataset(
        self,
        db,
        dataset_id: int,
        export_format: ExportFormat,
        current_user,
    ) -> DatasetExportResponse:

        # ----------------------------------------
        # Verify dataset ownership
        # ----------------------------------------

        dataset = self.dataset_service.get_dataset(
            db=db,
            dataset_id=dataset_id,
            current_user=current_user,
        )

        # ----------------------------------------
        # Fetch approved annotations
        # ----------------------------------------

        annotations = (
            self.annotation_repository
            .find_approved_annotations(
                db=db,
                dataset_id=dataset.id,
            )
        )

        # ----------------------------------------
        # Download all images
        # ----------------------------------------

        image_folder = (
            f"datasets/"
            f"project_{dataset.project_id}/"
            f"dataset_{dataset.id}/"
            f"images"
        )

        images = self.storage.download_files(
            image_folder,
        )

        # ----------------------------------------
        # Generate export files
        # ----------------------------------------

        if export_format == ExportFormat.YOLO:

            export_files = self.yolo.build_labels(
                annotations,
            )

        elif export_format == ExportFormat.COCO:

            export_files = {
                "annotations.json":
                    self.coco.build(
                        annotations,
                    )
            }

        elif export_format == ExportFormat.VOC:

            export_files = self.voc.build(
                annotations,
            )

        else:

            raise ValueError(
                "Unsupported export format."
            )

        # ----------------------------------------
        # Build ZIP
        # ----------------------------------------

        zip_bytes = self.zipper.create_zip(
            images=images,
            export_files=export_files,
        )

        # ----------------------------------------
        # Upload ZIP
        # ----------------------------------------

        zip_blob = (
            f"datasets/"
            f"project_{dataset.project_id}/"
            f"dataset_{dataset.id}/"
            f"exports/"
            f"{export_format.value}.zip"
        )

        download_url = self.storage.upload_file(
            blob_path=zip_blob,
            data=zip_bytes,
        )

        # ----------------------------------------
        # Response
        # ----------------------------------------

        return DatasetExportResponse(
            dataset_id=dataset.id,
            format=export_format,
            download_url=download_url,
        )