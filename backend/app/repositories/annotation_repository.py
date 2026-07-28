from sqlalchemy.orm import Session

from app.models.annotation import (
    Annotation,
    AnnotationStatus,
)
from app.repositories.base_repository import BaseRepository


class AnnotationRepository(BaseRepository[Annotation]):
    """
    Repository for Annotation persistence.
    """

    def __init__(self):
        super().__init__(Annotation)

    def find_by_id(
        self,
        db: Session,
        annotation_id: int,
    ) -> Annotation | None:

        return (
            db.query(Annotation)
            .filter(
                Annotation.id == annotation_id
            )
            .first()
        )

    def find_by_dataset(
        self,
        db: Session,
        dataset_id: int,
    ) -> list[Annotation]:

        return (
            db.query(Annotation)
            .filter(
                Annotation.dataset_id == dataset_id
            )
            .all()
        )

    def find_by_image(
        self,
        db: Session,
        dataset_id: int,
        image_name: str,
    ) -> list[Annotation]:

        return (
            db.query(Annotation)
            .filter(
                Annotation.dataset_id == dataset_id,
                Annotation.image_name == image_name,
            )
            .all()
        )

    def find_approved_annotations(
        self,
        db: Session,
        dataset_id: int,
    ) -> list[Annotation]:

        return (
            db.query(Annotation)
            .filter(
                Annotation.dataset_id == dataset_id,
                Annotation.status == AnnotationStatus.APPROVED,
            )
            .all()
        )

    def update(
        self,
        db: Session,
        annotation: Annotation,
    ) -> Annotation:

        db.add(annotation)
        db.commit()
        db.refresh(annotation)

        return annotation

    def find_approved_annotations(
    self,
    db: Session,
    dataset_id: int,
):
        return (
        db.query(Annotation)
        .filter(
            Annotation.dataset_id == dataset_id,
            Annotation.status == AnnotationStatus.APPROVED,
        )
        .all()
    )


    def find_dataset_annotations(
    self,
    db: Session,
    dataset_id: int,
):
        return (
        db.query(Annotation)
        .filter(
            Annotation.dataset_id == dataset_id,
        )
        .all()
    )