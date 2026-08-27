from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.dataset import Dataset
from app.models.inference_runs import InferenceRun
from app.models.model_registry import ModelRegistry
from app.models.project import Project
from app.models.user import User


class DashboardService:
    """
    Provides aggregated statistics for the authenticated user.
    """

    def get_statistics(
        self,
        db: Session,
        current_user: User,
    ) -> dict[str, int]:

        # ---------------------------------------------
        # Projects
        # ---------------------------------------------

        project_count = (
            db.query(func.count(Project.id))
            .filter(
                Project.owner_id == current_user.id
            )
            .scalar()
            or 0
        )

        # ---------------------------------------------
        # Datasets
        #
        # Dataset -> Project -> User
        # ---------------------------------------------

        dataset_count = (
            db.query(func.count(Dataset.id))
            .join(
                Project,
                Dataset.project_id == Project.id,
            )
            .filter(
                Project.owner_id == current_user.id
            )
            .scalar()
            or 0
        )

        # ---------------------------------------------
        # Models
        #
        # ModelRegistry -> Dataset -> Project -> User
        # ---------------------------------------------

        model_count = (
            db.query(func.count(ModelRegistry.id))
            .join(
                Dataset,
                ModelRegistry.dataset_id == Dataset.id,
            )
            .join(
                Project,
                Dataset.project_id == Project.id,
            )
            .filter(
                Project.owner_id == current_user.id
            )
            .scalar()
            or 0
        )

        # ---------------------------------------------
        # Inference Runs
        #
        # InferenceRun has user_id directly.
        # ---------------------------------------------

        inference_run_count = (
            db.query(func.count(InferenceRun.id))
            .filter(
                InferenceRun.user_id == current_user.id
            )
            .scalar()
            or 0
        )

        return {
            "projects": project_count,
            "datasets": dataset_count,
            "models": model_count,
            "inference_runs": inference_run_count,
        }