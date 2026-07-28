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
from app.schemas.export import (
    DatasetExportResponse,
    ExportFormat,
)
from app.services.export_services import ExportService


router = APIRouter(
    prefix="/datasets",
    tags=["Dataset Export"],
)

export_service = ExportService()


@router.get(
    "/{dataset_id}/export",
    response_model=DatasetExportResponse,
    status_code=status.HTTP_200_OK,
)
def export_dataset(
    dataset_id: int,
    format: ExportFormat,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Export a dataset in YOLO, COCO or Pascal VOC format.
    """

    try:

        return export_service.export_dataset(
            db=db,
            dataset_id=dataset_id,
            export_format=format,
            current_user=current_user,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )