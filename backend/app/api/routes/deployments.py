from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.services.deployment_services import (
    DeploymentService,
    DeploymentException,
)

# Use your existing authentication dependency
from app.auth.dependencies import (
    get_current_user,
)


router = APIRouter(
    prefix="/models",
    tags=["Model Deployment"],
)


def get_deployment_service(
    db: Session = Depends(get_db),
):
    return DeploymentService(db)


# ==========================================================
# Deploy Model
# ==========================================================

@router.post(
    "/{model_id}/deploy",
)
def deploy_model(
    model_id: int,

    endpoint_name: str | None = None,

    deployment_name: str | None = None,

    instance_type: str | None = None,

    instance_count: int | None = None,

    current_user: User = Depends(
        get_current_user
    ),

    service: DeploymentService = Depends(
        get_deployment_service
    ),
):

    try:

        return service.deploy_model(
            model_id=model_id,

            current_user=current_user,

            endpoint_name=endpoint_name,

            deployment_name=deployment_name,

            instance_type=instance_type,

            instance_count=instance_count,
        )

    except PermissionError as exc:

        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )

    except DeploymentException as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )