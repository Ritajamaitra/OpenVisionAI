from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.experiment import (
    ExperimentDetails,
    ExperimentSummary,
)
from app.integrations.azureml.azure_ml import azure_ml
from app.services.experiment_services import (
    ExperimentNotFoundException,
    ExperimentService,
)

router = APIRouter(
    prefix="/experiments",
    tags=["Experiments"],
)


def get_experiment_service() -> ExperimentService:
    """
    Dependency that provides an ExperimentService instance.
    """
    ml_client = azure_ml.client
    return ExperimentService(ml_client)


@router.get(
    "",
    response_model=list[ExperimentSummary],
    summary="List all experiment runs",
)
def list_experiments(
    service: ExperimentService = Depends(get_experiment_service),
):
    """
    Retrieve all Azure ML experiment runs.
    """
    return service.list_experiments()


@router.get(
    "/{run_id}",
    response_model=ExperimentDetails,
    summary="Get experiment details",
)
def get_experiment(
    run_id: str,
    service: ExperimentService = Depends(get_experiment_service),
):
    """
    Retrieve details for a specific experiment run.
    """
    try:
        return service.get_experiment(run_id)

    except ExperimentNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.get(
    "/projects/{project_id}",
    response_model=list[ExperimentSummary],
    summary="List experiments for a project",
)
def list_project_experiments(
    project_id: int,
    service: ExperimentService = Depends(get_experiment_service),
):
    """
    Retrieve all experiment runs for a specific project.
    """
    return service.list_experiments(project_id=project_id)