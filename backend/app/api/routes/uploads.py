from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import Response
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
    "/datasets/{dataset_id}/images",
    response_model=list[str],
)
def list_dataset_images(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return image filenames stored for a dataset."""
    try:
        return upload_service.list_dataset_images(
            db=db,
            dataset_id=dataset_id,
            current_user=current_user,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )


@router.get(
    "/datasets/{dataset_id}/images/{image_name}",
)
def get_dataset_image(
    dataset_id: int,
    image_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Stream one dataset image through the authenticated API."""
    try:
        image_bytes, content_type = upload_service.get_dataset_image(
            db=db,
            dataset_id=dataset_id,
            image_name=image_name,
            current_user=current_user,
        )

        return Response(
            content=image_bytes,
            media_type=content_type,
            headers={"Cache-Control": "private, max-age=300"},
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        # Blob not found / storage failure.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image '{image_name}' could not be retrieved.",
        ) from exc


@router.get(
    "/datasets/{dataset_id}/preview",
    response_model=DatasetPreviewResponse,
)
def preview_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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
