from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.upload import (
    DatasetPreviewResponse,
    UploadAnnotationResponse,
    UploadImageResponse,
)
from app.services.upload_services import UploadService

router = APIRouter(
    tags=["Uploads"],
)

upload_service = UploadService()


@router.post(
    "/datasets/{dataset_id}/images",
    response_model=UploadImageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_image(
    dataset_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload an image to a dataset.
    """

    try:
        return await upload_service.upload_image(
            db=db,
            dataset_id=dataset_id,
            file=file,
            current_user=current_user,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )


@router.post(
    "/datasets/{dataset_id}/annotations",
    response_model=UploadAnnotationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_annotation(
    dataset_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload an annotation file.
    """

    try:
        return await upload_service.upload_annotation(
            db=db,
            dataset_id=dataset_id,
            file=file,
            current_user=current_user,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )


@router.get(
    "/datasets/{dataset_id}/preview",
    response_model=DatasetPreviewResponse,
)
def preview_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Preview dataset statistics.
    """

    try:
        return upload_service.preview_dataset(
            db=db,
            dataset_id=dataset_id,
            current_user=current_user,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )