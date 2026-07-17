from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseEntity
from app.models.project_status import ProjectStatus
from app.models.user import User
from app.models.dataset import Dataset
from app.models.report import Report

class Project(BaseEntity):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus),
        nullable=False,
        default=ProjectStatus.ACTIVE,
    )

    owner: Mapped[User] = relationship(
        "User",
        back_populates="projects",
    )

    datasets: Mapped[list["Dataset"]] = relationship(
        "Dataset",
        back_populates="project",
    )

    reports: Mapped[list["Report"]] = relationship(
        "Report",
        back_populates="project",
    )