from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.model import (
    ModelCreate,
    ModelResponse,
    ModelUpdate,
)
from app.services.model_services import ModelService

router = APIRouter(
    tags=["Models"],
)

model_service = ModelService()


@router.post(
    "/datasets/{dataset_id}/models",
    response_model=ModelResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_model(
    dataset_id: int,
    model: ModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a model under a dataset.
    """
    try:
        return model_service.create_model(
            db=db,
            model_data=model,
            dataset_id=dataset_id,
            current_user=current_user,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )


@router.get(
    "/datasets/{dataset_id}/models",
    response_model=list[ModelResponse],
)
def get_dataset_models(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List every model belonging to a dataset.
    """
    try:
        return model_service.get_dataset_models(
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
    "/models/{model_id}",
    response_model=ModelResponse,
)
def get_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a model.
    """
    try:
        return model_service.get_model(
            db=db,
            model_id=model_id,
            current_user=current_user,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )


@router.put(
    "/models/{model_id}",
    response_model=ModelResponse,
)
def update_model(
    model_id: int,
    model: ModelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update model metadata.
    """
    try:
        return model_service.update_model(
            db=db,
            model_id=model_id,
            model_update=model,
            current_user=current_user,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )


@router.delete(
    "/models/{model_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a model.
    """
    try:
        model_service.delete_model(
            db=db,
            model_id=model_id,
            current_user=current_user,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )