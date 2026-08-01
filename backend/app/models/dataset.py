from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    func,
)
from app.models.base import BaseEntity
from app.models.project import Project
from app.models.model_registry import ModelRegistry
from app.models.dataset_status import DatasetStatus
class Dataset(BaseEntity):
    __tablename__ = "datasets"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False,
    )

    storage_path: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    dataset_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    total_images: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    total_annotations: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    status: Mapped[DatasetStatus] = mapped_column(
        Enum(DatasetStatus),
        nullable=False,
        default=DatasetStatus.ACTIVE,
    )

    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="datasets",
    )

    models: Mapped[list["ModelRegistry"]] = relationship(
        "ModelRegistry",
        back_populates="dataset",
    )

    annotations = relationship(
    "Annotation",
    backref="dataset",
    cascade="all, delete-orphan",
)

    annotated_images = Column(
    Integer,
    nullable=False,
    default=0,
)

    total_classes = Column(
    Integer,
    nullable=False,
    default=0,
)

    last_updated = Column(
    DateTime,
    nullable=False,
    server_default=func.now(),
    onupdate=func.now(),
)
    training_runs = relationship(
    "TrainingRun",
    back_populates="dataset",
    cascade="all, delete-orphan",
)

