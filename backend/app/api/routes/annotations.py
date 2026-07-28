from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User

from app.schemas.annotation import (
    AutoAnnotationRequest,
    AutoAnnotationResponse,
    AnnotationReview,
    AnnotationResponse,
    AnnotationListResponse,
)

from app.services.auto_annotation_services import AutoAnnotationService
from app.services.annotation_services import AnnotationService


router = APIRouter(
    tags=["Annotations"],
)

auto_annotation_service = AutoAnnotationService()
annotation_service = AnnotationService()


@router.post(
    "/datasets/{dataset_id}/images/{image_name}/annotate",
    response_model=AutoAnnotationResponse,
)
async def annotate_image(
    dataset_id: int,
    image_name: str,
    request: AutoAnnotationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:

        return await auto_annotation_service.annotate_image(
            db=db,
            dataset_id=dataset_id,
            image_name=image_name,
            request=request,
            current_user=current_user,
        )

    except Exception as exc:

        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.get(
    "/annotations/{annotation_id}",
    response_model=AnnotationResponse,
)
def get_annotation(
    annotation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:

        return annotation_service.get_annotation(
            db=db,
            annotation_id=annotation_id,
            current_user=current_user,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.put(
    "/annotations/{annotation_id}/review",
    response_model=AnnotationResponse,
)
def review_annotation(
    annotation_id: int,
    review: AnnotationReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:

        return annotation_service.review_annotation(
            db=db,
            annotation_id=annotation_id,
            review=review,
            current_user=current_user,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )



@router.get(
    "/datasets/{dataset_id}/annotations",
    response_model=AnnotationListResponse,
)
def get_dataset_annotations(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    annotations = annotation_service.get_dataset_annotations(
        db=db,
        dataset_id=dataset_id,
        current_user=current_user,
    )

    return AnnotationListResponse(
        annotations=annotations,
        total=len(annotations),
    )



@router.get(
    "/datasets/{dataset_id}/images/{image_name}/annotations",
    response_model=AnnotationListResponse,
)
def get_image_annotations(
    dataset_id: int,
    image_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    annotations = annotation_service.get_image_annotations(
        db=db,
        dataset_id=dataset_id,
        image_name=image_name,
        current_user=current_user,
    )

    return AnnotationListResponse(
        annotations=annotations,
        total=len(annotations),
    )