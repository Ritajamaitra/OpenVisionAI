from sqlalchemy.orm import Session

from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.services.base_services import BaseService


class ProjectService(BaseService[Project]):
    """
    Business logic related to projects.
    """

    def __init__(self):
        super().__init__(ProjectRepository())

    def create_project(
        self,
        db: Session,
        project: Project,
    ) -> Project:
        """
        Future business rules can be added here.
        """

        return self.repository.create(db, project)

    def get_projects_by_owner(
        self,
        db: Session,
        owner_id: int,
    ) -> list[Project]:
        return self.repository.find_by_owner(db, owner_id)

    def get_active_projects(
        self,
        db: Session,
    ) -> list[Project]:
        return self.repository.find_active_projects(db)