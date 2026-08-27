from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.deployment import (
    DeploymentCreate,
    DeploymentResponse,
    EndpointResponse,
)
from app.services.deployment_services import (
    DeploymentException,
    DeploymentService,
)

router = APIRouter(
    prefix="/deployments",
    tags=["Deployments"],
)


def get_deployment_service(
    db: Session = Depends(get_db),
) -> DeploymentService:
    return DeploymentService(db)


@router.post(
    "/models/{model_id}",
    response_model=DeploymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def deploy_model(
    model_id: int,
    request: DeploymentCreate | None = None,
    service: DeploymentService = Depends(
        get_deployment_service
    ),
    current_user: User = Depends(get_current_user),
):
    request = request or DeploymentCreate()

    try:
        return service.deploy_model(
            model_id=model_id,
            current_user=current_user,
            endpoint_name=request.endpoint_name,
            deployment_name=request.deployment_name,
            instance_type=request.instance_type,
            instance_count=request.instance_count,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except DeploymentException as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


@router.get(
    "/management",
    response_model=list[DeploymentResponse],
)
def list_deployments(
    service: DeploymentService = Depends(
        get_deployment_service
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.list_user_deployments(
            current_user=current_user
        )

    except DeploymentException as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


@router.get(
    "/{endpoint_name}",
    response_model=DeploymentResponse,
)
def get_deployment(
    endpoint_name: str,
    service: DeploymentService = Depends(
        get_deployment_service
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.get_endpoint(
            endpoint_name=endpoint_name,
            current_user=current_user,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{endpoint_name}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def stop_deployment(
    endpoint_name: str,
    service: DeploymentService = Depends(
        get_deployment_service
    ),
    current_user: User = Depends(get_current_user),
):
    try:
        service.stop_endpoint(
            endpoint_name=endpoint_name,
            current_user=current_user,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except DeploymentException as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
