from sqlalchemy.orm import Session

from app.models.project import Project, ProjectStatus
from app.models.user import User
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
)
from app.services.base_services import BaseService


class ProjectService(BaseService[Project]):
    """
    Business logic for project management.
    """

    def __init__(self):
        super().__init__(ProjectRepository())

    def create_project(
        self,
        db: Session,
        project_data: ProjectCreate,
        current_user: User,
    ) -> Project:
        """
        Create a new project owned by the authenticated user.
        """

        existing_project = self.repository.find_by_owner_and_name(
            db=db,
            owner_id=current_user.id,
            name=project_data.name,
        )

        if existing_project is not None:
            raise PermissionError(
                "A project with this name already exists for this user."
            )

        project = Project(
            name=project_data.name,
            description=project_data.description,
            owner_id=current_user.id,
            status=ProjectStatus.ACTIVE,
        )

        return self.repository.create(
            db=db,
            obj=project,
        )

    def get_project(
        self,
        db: Session,
        project_id: int,
        current_user: User,
    ) -> Project:
        """
        Return a project only if it belongs to the authenticated user.
        """

        project = self.repository.find_by_id_and_owner(
            db=db,
            project_id=project_id,
            owner_id=current_user.id,
        )

        if project is None:
            raise PermissionError(
                "Project not found or access denied."
            )

        return project

    def get_user_projects(
        self,
        db: Session,
        current_user: User,
    ) -> list[Project]:
        """
        Return all projects owned by the current user.
        """

        return self.repository.find_by_owner(
            db=db,
            owner_id=current_user.id,
        )

    def update_project(
        self,
        db: Session,
        project_id: int,
        project_update: ProjectUpdate,
        current_user: User,
    ) -> Project:
        """
        Update only the supplied fields.
        Ownership cannot be changed.
        """

        project = self.get_project(
            db=db,
            project_id=project_id,
            current_user=current_user,
        )

        if project_update.name is not None:
            project.name = project_update.name

        if project_update.description is not None:
            project.description = project_update.description

        return self.repository.update(
            db=db,
            obj=project,
        )

    def delete_project(
        self,
        db: Session,
        project_id: int,
        current_user: User,
    ) -> None:
        """
        Delete a project owned by the authenticated user.
        """

        project = self.get_project(
            db=db,
            project_id=project_id,
            current_user=current_user,
        )

        self.repository.delete(
            db=db,
            obj=project,
        )