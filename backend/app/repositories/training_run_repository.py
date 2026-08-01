from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.training_run import TrainingRun
from app.schemas.training_run import (
    TrainingRunCreate,
    TrainingRunUpdate,
)


class TrainingRunRepository:

    def __init__(self, db: Session):
        self.db = db

    # ==========================================================
    # Create
    # ==========================================================

    def create(
        self,
        request: TrainingRunCreate,
    ) -> TrainingRun:

        training_run = TrainingRun(
            project_id=request.project_id,
            dataset_id=request.dataset_id,
            submitted_by=request.submitted_by,
            azure_run_id=request.azure_run_id,
            experiment_name=request.experiment_name,
            model_name=request.model_name,
            status=request.status,
            precision=request.precision,
            recall=request.recall,
            map50=request.map50,
            map50_95=request.map50_95,
            training_time=request.training_time,
            registered_model_name=request.registered_model_name,
            registered_model_version=request.registered_model_version,
            endpoint_name=request.endpoint_name,
        )

        self.db.add(training_run)
        self.db.commit()
        self.db.refresh(training_run)

        return training_run

    # ==========================================================
    # List
    # ==========================================================

    def list(self) -> List[TrainingRun]:

        return (
            self.db.query(TrainingRun)
            .order_by(TrainingRun.created_at.desc())
            .all()
        )

    # ==========================================================
    # Get by Azure Run ID
    # ==========================================================

    def get_by_run_id(
        self,
        azure_run_id: str,
    ) -> Optional[TrainingRun]:

        return (
            self.db.query(TrainingRun)
            .filter(
                TrainingRun.azure_run_id == azure_run_id
            )
            .first()
        )

    # ==========================================================
    # List Project Runs
    # ==========================================================

    def list_by_project(
        self,
        project_id: int,
    ) -> List[TrainingRun]:

        return (
            self.db.query(TrainingRun)
            .filter(
                TrainingRun.project_id == project_id
            )
            .order_by(
                TrainingRun.created_at.desc()
            )
            .all()
        )

    # ==========================================================
    # Update
    # ==========================================================

    def update(
        self,
        training_run: TrainingRun,
        update: TrainingRunUpdate,
    ) -> TrainingRun:

        values = update.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )

        for key, value in values.items():
            setattr(training_run, key, value)

        self.db.commit()
        self.db.refresh(training_run)

        return training_run

    # ==========================================================
    # Delete
    # ==========================================================

    def delete(
        self,
        training_run: TrainingRun,
    ) -> None:

        self.db.delete(training_run)
        self.db.commit()

    # ==========================================================
    # Exists
    # ==========================================================

    def exists(
        self,
        azure_run_id: str,
    ) -> bool:

        return (
            self.db.query(TrainingRun)
            .filter(
                TrainingRun.azure_run_id == azure_run_id
            )
            .first()
            is not None
        )

    # ==========================================================
    # Running
    # ==========================================================

    def running(self) -> List[TrainingRun]:

        return (
            self.db.query(TrainingRun)
            .filter(
                TrainingRun.status == "RUNNING"
            )
            .all()
        )

    # ==========================================================
    # Completed
    # ==========================================================

    def completed(self) -> List[TrainingRun]:

        return (
            self.db.query(TrainingRun)
            .filter(
                TrainingRun.status == "COMPLETED"
            )
            .all()
        )

    # ==========================================================
    # Failed
    # ==========================================================

    def failed(self) -> List[TrainingRun]:

        return (
            self.db.query(TrainingRun)
            .filter(
                TrainingRun.status == "FAILED"
            )
            .all()
        )