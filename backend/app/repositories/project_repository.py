from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_status import ProjectStatus
from app.repositories.base_repository import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self):
        super().__init__(Project)

    def find_by_owner(
        self,
        db: Session,
        owner_id: int,
    ) -> list[Project]:
        return (
            db.query(Project)
            .filter(Project.owner_id == owner_id)
            .all()
        )

    def find_by_owner_and_name(
        self,
        db: Session,
        owner_id: int,
        name: str,
    ) -> Project | None:
        return (
            db.query(Project)
            .filter(
                Project.owner_id == owner_id,
                Project.name == name,
            )
            .first()
        )

    def find_active_projects(
        self,
        db: Session,
    ) -> list[Project]:
        return (
            db.query(Project)
            .filter(Project.status == ProjectStatus.ACTIVE)
            .all()
        )

    def find_by_id_and_owner(
        self,
        db: Session,
        project_id: int,
        owner_id: int,
    ) -> Project | None:
        return (
            db.query(Project)
            .filter(
                Project.id == project_id,
                Project.owner_id == owner_id,
            )
            .first()
        )