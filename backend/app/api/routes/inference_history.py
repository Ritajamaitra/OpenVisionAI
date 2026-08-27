from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.repositories.inference_run_repository import InferenceRunRepository

router = APIRouter(tags=["Inference"])


@router.get("/inference/runs")
def list_inference_runs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repository = InferenceRunRepository()

    runs = repository.find_by_user(
        db=db,
        user_id=current_user.id,
    )

    return [
        {
            "id": run.id,
            "model_id": run.model_registry_id,
            "model_name": run.model_registry.name,
            "model_version": str(run.model_version),
            "status": run.status,
            "confidence_threshold": run.confidence_threshold,
            "prediction_count": run.prediction_count,
            "predictions": run.predictions_json or [],
            "inference_latency_ms": run.inference_latency_ms,
            "input_filename": run.input_filename,
            "input_content_type": run.input_content_type,
            "error_message": run.error_message,
            "created_at": run.created_at,
        }
        for run in runs
    ]

