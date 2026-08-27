"""
OpenVisionAI Training API

Responsibilities
----------------
1. Accept training requests
2. Authenticate the caller
3. Delegate training orchestration to TrainingService
4. Expose training run status and lifecycle endpoints

The route layer contains no Azure ML SDK logic.
"""

from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.training_run import (
    TrainingRunResponse,
    TrainingRunSummary,
    TrainingRunUpdate,
)
from app.services.training_run_services import (
    ModelRegistrationException,
    TrainingRunAlreadyExistsException,
    TrainingRunNotFoundException,
    TrainingSubmissionException,
    TrainingService,
)


router = APIRouter(
    prefix="/training",
    tags=["Training"],
)


# ==========================================================
# Request Contract
# ==========================================================


class TrainingJobRequest(BaseModel):
    """
    API request for launching an Azure ML training job.

    The caller supplies only training configuration.
    Azure-specific environment and compute configuration remain
    inside TrainingService.
    """

    project_id: int = Field(
        ...,
        description="OpenVisionAI project ID.",
    )

    dataset_id: int = Field(
        ...,
        description="Dataset to train on.",
    )

    model_name: str = Field(
        default="yolov8n.pt",
        min_length=1,
        description="YOLO model checkpoint.",
    )

    epochs: int = Field(
        default=50,
        ge=1,
        description="Number of training epochs.",
    )

    imgsz: int = Field(
        default=640,
        ge=32,
        description="Training image size.",
    )

    batch: int = Field(
        default=16,
        ge=1,
        description="Training batch size.",
    )


# ==========================================================
# Dependency
# ==========================================================


def get_training_service(
    db: Session = Depends(get_db),
) -> TrainingService:
    return TrainingService(db)


# ==========================================================
# Submit Training
# ==========================================================


@router.post(
    "/jobs",
    response_model=TrainingRunResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit an Azure ML training job",
)
def submit_training_job(
    request: TrainingJobRequest,
    service: TrainingService = Depends(
        get_training_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Submit a training job through the complete orchestration flow.

    Project
        ↓
    Dataset
        ↓
    YOLO Export
        ↓
    Azure ML Job
        ↓
    TrainingRun
    """

    try:
        return service.submit_training(
            project_id=request.project_id,
            dataset_id=request.dataset_id,
            model_name=request.model_name,
            epochs=request.epochs,
            imgsz=request.imgsz,
            batch=request.batch,
            current_user=current_user,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except TrainingRunAlreadyExistsException as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except TrainingSubmissionException as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


# ==========================================================
# List Training Runs
# ==========================================================


@router.get(
    "/jobs",
    response_model=List[TrainingRunSummary],
    summary="List training runs",
)
def list_training_jobs(
    service: TrainingService = Depends(
        get_training_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    """
    List training runs.

    The service currently owns the repository-level list operation.
    """
    return service.list_training_runs()


# ==========================================================
# Project Training Runs
# ==========================================================


@router.get(
    "/jobs/project/{project_id}",
    response_model=List[TrainingRunSummary],
    summary="List training runs for a project",
)
def list_project_training_jobs(
    project_id: int,
    service: TrainingService = Depends(
        get_training_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        return service.list_project_training_runs(
            project_id=project_id,
            current_user=current_user,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


# ==========================================================
# Get Training Run
# ==========================================================


@router.get(
    "/jobs/{azure_run_id}",
    response_model=TrainingRunResponse,
    summary="Get a training run",
)
def get_training_job(
    azure_run_id: str,
    service: TrainingService = Depends(
        get_training_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        return service.get_training_run(
            azure_run_id
        )

    except TrainingRunNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


# ==========================================================
# Register Trained Model
# ==========================================================


@router.post(
    "/jobs/{azure_run_id}/register-model",
    response_model=TrainingRunResponse,
    summary="Register the trained model in Azure ML",
)
def register_training_model(
    azure_run_id: str,
    service: TrainingService = Depends(
        get_training_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        return service.register_model(
            azure_run_id=azure_run_id
        )

    except TrainingRunNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ModelRegistrationException as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


# ==========================================================
# Synchronize Training Run
# ==========================================================


@router.post(
    "/jobs/{azure_run_id}/sync",
    response_model=TrainingRunResponse,
    summary="Synchronize training run status and metrics",
)
def sync_training_job(
    azure_run_id: str,
    service: TrainingService = Depends(
        get_training_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        return service.sync_training_run(
            azure_run_id
        )

    except TrainingRunNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


# ==========================================================
# Cancel Training Run
# ==========================================================


@router.post(
    "/jobs/{azure_run_id}/cancel",
    response_model=TrainingRunResponse,
    summary="Cancel a training run",
)
def cancel_training_job(
    azure_run_id: str,
    service: TrainingService = Depends(
        get_training_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        return service.cancel_training_run(
            azure_run_id
        )

    except TrainingRunNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except TrainingSubmissionException as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


# ==========================================================
# Update Training Run
# ==========================================================


@router.patch(
    "/jobs/{azure_run_id}",
    response_model=TrainingRunResponse,
    summary="Update training run metadata",
)
def update_training_job(
    azure_run_id: str,
    update: TrainingRunUpdate,
    service: TrainingService = Depends(
        get_training_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        return service.update_training_run(
            azure_run_id=azure_run_id,
            update=update,
        )

    except TrainingRunNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


# ==========================================================
# Delete Training Run
# ==========================================================


@router.delete(
    "/jobs/{azure_run_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a training run record",
)
def delete_training_job(
    azure_run_id: str,
    service: TrainingService = Depends(
        get_training_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        service.delete_training_run(
            azure_run_id
        )

    except TrainingRunNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc