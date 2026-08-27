import json
import time

from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.ai.builders.coco_builder import COCOBuilder
from app.ai.detectors.detector_factory import DetectorFactory
from app.ai.io.imageloader import ImageLoader
from app.models.user import User
from app.schemas.annotation import (
    AutoAnnotationRequest,
    AutoAnnotationResponse,
)
from app.services.dataset_services import DatasetService
from app.storage.azure_storage_blob import AzureBlobStorage
from app.models.annotation import (
    Annotation,
    AnnotationStatus,
)

class AutoAnnotationService:

    def __init__(
        self,
        dataset_service: DatasetService | None = None,
        storage: AzureBlobStorage | None = None,
        builder: COCOBuilder | None = None,
    ):
        self.dataset_service = dataset_service or DatasetService()
        self.storage = storage or AzureBlobStorage()
        self.builder = builder or COCOBuilder()

    async def annotate_image(
        self,
        db: Session,
        dataset_id: int,
        image_name: str,
        request: AutoAnnotationRequest,
        current_user: User,
    ) -> AutoAnnotationResponse:

        dataset = self.dataset_service.get_dataset(
            db=db,
            dataset_id=dataset_id,
            current_user=current_user,
        )

        blob_path = (
            f"datasets/"
            f"project_{dataset.project_id}/"
            f"dataset_{dataset.id}/"
            f"images/"
            f"{image_name}"
        )

        image_bytes, _ = self.storage.download_dataset_image(
            blob_path
        )

        image = ImageLoader.load(image_bytes)

        detector = DetectorFactory.get_detector(
            request.model
        )

        start = time.perf_counter()

        detections = detector.predict(
            image=image,
            prompt=request.prompt,
            confidence=request.confidence,
        )
                # ------------------------------------------------------------
        # Remove previous AUTO_GENERATED annotations for this image
        # ------------------------------------------------------------
        #
        # Approved annotations are intentionally preserved.
        # This makes Auto Annotate safe to run multiple times without
        # continuously creating duplicate pending annotations.
        #
        db.query(Annotation).filter(
            and_(
                Annotation.dataset_id == dataset.id,
                Annotation.image_name == image_name,
                Annotation.status == AnnotationStatus.AUTO_GENERATED,
            )
        ).delete(synchronize_session=False)

        db.flush()
        for detection in detections:
            label = detection["label"].strip()
            if not label:
                continue

            x, y, width, height = detection["bbox"]
            annotation = Annotation(
                dataset_id=dataset.id,
                image_name=image_name,
                label=label,
                confidence=detection["confidence"],
                bbox_x=x,
                bbox_y=y,
                bbox_width=width,
                bbox_height=height,
                status=AnnotationStatus.AUTO_GENERATED,
            )

            db.add(annotation)

        db.flush()


        processing_time_ms = round(
            (time.perf_counter() - start) * 1000,
            2,
        )

        coco = self.builder.build(
            image_name=image_name,
            width=image.width,
            height=image.height,
            detections=detections,
        )

        annotation_name = (
            image_name.rsplit(".", 1)[0]
            + ".json"
        )

        annotation_path = (
            f"datasets/"
            f"project_{dataset.project_id}/"
            f"dataset_{dataset.id}/"
            f"annotations/"
            f"{annotation_name}"
        )

        annotation_bytes = json.dumps(
            coco,
            indent=2,
        ).encode("utf-8")

        uploaded_uri = self.storage.upload_file(
            blob_path=annotation_path,
            data=annotation_bytes,
        )

        dataset.total_annotations += len(
            detections
        )
        db.commit()
        db.refresh(dataset)

        return AutoAnnotationResponse(
            image_name=image_name,
            model=request.model,
            detections=len(detections),
            classes=sorted(
                {
                    d["label"]
                    for d in detections
                }
            ),
            annotation_uri=uploaded_uri,
            processing_time_ms=processing_time_ms,
        )