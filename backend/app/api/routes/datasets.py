from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.dataset import (
    DatasetCreate,
    DatasetResponse,
    DatasetUpdate,
)
from app.services.dataset_services import DatasetService

router = APIRouter(
    tags=["Datasets"],
)

dataset_service = DatasetService()


@router.post(
    "/projects/{project_id}/datasets",
    response_model=DatasetResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_dataset(
    project_id: int,
    dataset: DatasetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a dataset inside a project.
    """
    try:
        return dataset_service.create_dataset(
            db=db,
            dataset_data=dataset,
            project_id=project_id,
            current_user=current_user,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )


@router.get(
    "/projects/{project_id}/datasets",
    response_model=list[DatasetResponse],
)
def get_project_datasets(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return every dataset belonging to a project.
    """
    try:
        return dataset_service.get_project_datasets(
            db=db,
            project_id=project_id,
            current_user=current_user,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )


@router.get(
    "/datasets/{dataset_id}",
    response_model=DatasetResponse,
)
def get_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return a single dataset.
    """
    try:
        return dataset_service.get_dataset(
            db=db,
            dataset_id=dataset_id,
            current_user=current_user,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )


@router.put(
    "/datasets/{dataset_id}",
    response_model=DatasetResponse,
)
def update_dataset(
    dataset_id: int,
    dataset: DatasetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update dataset metadata.
    """
    try:
        return dataset_service.update_dataset(
            db=db,
            dataset_id=dataset_id,
            dataset_update=dataset,
            current_user=current_user,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )


@router.delete(
    "/datasets/{dataset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a dataset.
    """
    try:
        dataset_service.delete_dataset(
            db=db,
            dataset_id=dataset_id,
            current_user=current_user,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )