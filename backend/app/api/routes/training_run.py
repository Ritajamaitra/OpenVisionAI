from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.repositories.training_run_repository import (
    TrainingRunRepository,
)

from app.schemas.training_run import (
    TrainingRunCreate,
    TrainingRunResponse,
    TrainingRunSummary,
    TrainingRunUpdate,
)

from app.services.training_run_services import (
    TrainingRunAlreadyExistsException,
    TrainingRunNotFoundException,
    TrainingRunService,
)

router = APIRouter(
    prefix="/training-runs",
    tags=["Training Runs"],
)


# ==========================================================
# Dependency
# ==========================================================

def get_service(
    db: Session = Depends(get_db),
) -> TrainingRunService:

    repository = TrainingRunRepository(db)

    return TrainingRunService(repository)


# ==========================================================
# Create
# ==========================================================

@router.post(
    "",
    response_model=TrainingRunResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_training_run(
    request: TrainingRunCreate,
    service: TrainingRunService = Depends(get_service),
):

    try:
        return service.create_training_run(request)

    except TrainingRunAlreadyExistsException as ex:

        raise HTTPException(
            status_code=409,
            detail=str(ex),
        )


# ==========================================================
# List
# ==========================================================

@router.get(
    "",
    response_model=List[TrainingRunSummary],
)
def list_training_runs(
    service: TrainingRunService = Depends(get_service),
):

    return service.list_training_runs()


# ==========================================================
# Get
# ==========================================================

@router.get(
    "/{azure_run_id}",
    response_model=TrainingRunResponse,
)
def get_training_run(
    azure_run_id: str,
    service: TrainingRunService = Depends(get_service),
):

    try:

        return service.get_training_run(
            azure_run_id,
        )

    except TrainingRunNotFoundException as ex:

        raise HTTPException(
            status_code=404,
            detail=str(ex),
        )


# ==========================================================
# Project Runs
# ==========================================================

@router.get(
    "/project/{project_id}",
    response_model=List[TrainingRunSummary],
)
def list_project_training_runs(
    project_id: int,
    service: TrainingRunService = Depends(get_service),
):

    return service.list_project_training_runs(
        project_id,
    )


# ==========================================================
# Update
# ==========================================================

@router.patch(
    "/{azure_run_id}",
    response_model=TrainingRunResponse,
)
def update_training_run(
    azure_run_id: str,
    update: TrainingRunUpdate,
    service: TrainingRunService = Depends(get_service),
):

    try:

        return service.update_training_run(
            azure_run_id,
            update,
        )

    except TrainingRunNotFoundException as ex:

        raise HTTPException(
            status_code=404,
            detail=str(ex),
        )


# ==========================================================
# Delete
# ==========================================================

@router.delete(
    "/{azure_run_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_training_run(
    azure_run_id: str,
    service: TrainingRunService = Depends(get_service),
):

    try:

        service.delete_training_run(
            azure_run_id,
        )

    except TrainingRunNotFoundException as ex:

        raise HTTPException(
            status_code=404,
            detail=str(ex),
        )