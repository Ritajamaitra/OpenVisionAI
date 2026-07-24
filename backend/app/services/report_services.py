from datetime import datetime

from sqlalchemy.orm import Session

from app.models.report import (
    Report,
    ReportStatus,
)
from app.models.user import User
from app.repositories.report_repository import ReportRepository
from app.schemas.report import (
    ReportCreate,
    ReportUpdate,
)
from app.services.base_services import BaseService
from app.services.model_services import ModelService
from app.services.project_services import ProjectService


class ReportService(BaseService[Report]):
    """
    Business logic for report management.
    """

    def __init__(self):
        super().__init__(ReportRepository())
        self.project_service = ProjectService()
        self.model_service = ModelService()

    def create_report(
        self,
        db: Session,
        report_data: ReportCreate,
        project_id: int,
        current_user: User,
    ) -> Report:
        """
        Create a report within a project owned by the authenticated user.
        """

        # Verify project ownership
        project = self.project_service.get_project(
            db=db,
            project_id=project_id,
            current_user=current_user,
        )

        # Verify model ownership
        model = self.model_service.get_model(
            db=db,
            model_id=report_data.model_registry_id,
            current_user=current_user,
        )

        # Ensure the model belongs to this project
        if model.dataset.project_id != project.id:
            raise PermissionError(
                "Model does not belong to the specified project."
            )

        report = Report(
            name=report_data.name,
            project_id=project.id,
            model_registry_id=model.id,
            report_type=report_data.report_type,
            report_uri=report_data.report_uri,
            generated_at=datetime.utcnow(),
            status=ReportStatus.GENERATED,
        )

        return self.repository.create(
            db=db,
            obj=report,
        )

    def get_report(
        self,
        db: Session,
        report_id: int,
        current_user: User,
    ) -> Report:
        """
        Retrieve a report owned by the authenticated user.
        """

        projects = self.project_service.get_user_projects(
            db=db,
            current_user=current_user,
        )

        for project in projects:

            report = self.repository.find_by_id_and_project(
                db=db,
                report_id=report_id,
                project_id=project.id,
            )

            if report is not None:
                return report

        raise PermissionError(
            "Report not found or access denied."
        )

    def get_project_reports(
        self,
        db: Session,
        project_id: int,
        current_user: User,
    ) -> list[Report]:
        """
        Retrieve all reports belonging to a project.
        """

        project = self.project_service.get_project(
            db=db,
            project_id=project_id,
            current_user=current_user,
        )

        return self.repository.find_by_project(
            db=db,
            project_id=project.id,
        )

    def update_report(
        self,
        db: Session,
        report_id: int,
        report_update: ReportUpdate,
        current_user: User,
    ) -> Report:
        """
        Update mutable report fields.
        """

        report = self.get_report(
            db=db,
            report_id=report_id,
            current_user=current_user,
        )

        if report_update.name is not None:
            report.name = report_update.name

        if report_update.report_type is not None:
            report.report_type = report_update.report_type

        if report_update.report_uri is not None:
            report.report_uri = report_update.report_uri

        if report_update.status is not None:
            report.status = report_update.status

        return self.repository.update(
            db=db,
            obj=report,
        )

    def delete_report(
        self,
        db: Session,
        report_id: int,
        current_user: User,
    ) -> None:
        """
        Delete a report owned by the authenticated user.
        """

        report = self.get_report(
            db=db,
            report_id=report_id,
            current_user=current_user,
        )

        self.repository.delete(
            db=db,
            obj=report,
        )