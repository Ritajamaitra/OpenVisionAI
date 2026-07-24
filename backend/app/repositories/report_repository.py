from sqlalchemy.orm import Session

from app.models.report import (
    Report,
    ReportStatus,
)
from app.repositories.base_repository import BaseRepository


class ReportRepository(BaseRepository[Report]):
    """
    Repository for Report-specific database operations.
    """

    def __init__(self):
        super().__init__(Report)

    def find_by_project(
        self,
        db: Session,
        project_id: int,
    ) -> list[Report]:
        """
        Retrieve all reports belonging to a project.
        """

        return (
            db.query(Report)
            .filter(
                Report.project_id == project_id,
            )
            .order_by(Report.created_at.desc())
            .all()
        )

    def find_by_model(
        self,
        db: Session,
        model_registry_id: int,
    ) -> list[Report]:
        """
        Retrieve all reports generated for a model.
        """

        return (
            db.query(Report)
            .filter(
                Report.model_registry_id == model_registry_id,
            )
            .order_by(Report.created_at.desc())
            .all()
        )

    def find_active_reports(
        self,
        db: Session,
    ) -> list[Report]:
        """
        Retrieve all active reports.
        """

        return (
            db.query(Report)
            .filter(
                Report.status == ReportStatus.ACTIVE,
            )
            .order_by(Report.created_at.desc())
            .all()
        )

    def find_by_id_and_project(
        self,
        db: Session,
        report_id: int,
        project_id: int,
    ) -> Report | None:
        """
        Retrieve a report only if it belongs to the specified project.
        """

        return (
            db.query(Report)
            .filter(
                Report.id == report_id,
                Report.project_id == project_id,
            )
            .first()
        )