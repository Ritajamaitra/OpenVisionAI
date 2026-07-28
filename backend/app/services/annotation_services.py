from datetime import datetime, UTC

from sqlalchemy.orm import Session

from app.models.annotation import Annotation
from app.models.user import User
from app.repositories.annotation_repository import AnnotationRepository
from app.schemas.annotation import AnnotationReview
from app.services.base_services import BaseService
from app.services.dataset_services import DatasetService


class AnnotationService(BaseService[Annotation]):

    def __init__(self):
        super().__init__(AnnotationRepository())

        self.dataset_service = DatasetService()

    def get_annotation(
        self,
        db: Session,
        annotation_id: int,
        current_user: User,
    ) -> Annotation:

        annotation = self.repository.find_by_id(
            db,
            annotation_id,
        )

        if annotation is None:
            raise ValueError(
                "Annotation not found."
            )

        self.dataset_service.get_dataset(
            db=db,
            dataset_id=annotation.dataset_id,
            current_user=current_user,
        )

        return annotation

    def review_annotation(
        self,
        db: Session,
        annotation_id: int,
        review: AnnotationReview,
        current_user: User,
    ) -> Annotation:

        annotation = self.get_annotation(
            db=db,
            annotation_id=annotation_id,
            current_user=current_user,
        )

        annotation.status = review.status

        annotation.reviewed_at = datetime.now(
            UTC
        )

        annotation.reviewed_by = current_user.id

        return self.repository.update(
            db=db,
            annotation=annotation,
        )

    def get_dataset_annotations(
        self,
        db: Session,
        dataset_id: int,
        current_user: User,
    ) -> list[Annotation]:

        self.dataset_service.get_dataset(
            db=db,
            dataset_id=dataset_id,
            current_user=current_user,
        )

        return self.repository.find_by_dataset(
            db,
            dataset_id,
        )

    def get_image_annotations(
        self,
        db: Session,
        dataset_id: int,
        image_name: str,
        current_user: User,
    ) -> list[Annotation]:

        self.dataset_service.get_dataset(
            db=db,
            dataset_id=dataset_id,
            current_user=current_user,
        )

        return self.repository.find_by_image(
            db,
            dataset_id,
            image_name,
        )