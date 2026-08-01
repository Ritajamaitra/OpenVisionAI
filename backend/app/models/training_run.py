from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.models.base import BaseEntity


class TrainingRun(BaseEntity):
    __tablename__ = "training_runs"

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
    )

    dataset_id = Column(
        Integer,
        ForeignKey("datasets.id"),
        nullable=False,
    )

    submitted_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    # Azure ML
    azure_run_id = Column(
        String(255),
        nullable=True,
        unique=True,
    )

    azure_job_name = Column(
        String(255),
        nullable=True,
    )

    experiment_name = Column(
        String(255),
        nullable=True,
    )

    # Model Information
    model_name = Column(
        String(255),
        nullable=True,
    )

    registered_model_name = Column(
        String(255),
        nullable=True,
    )

    registered_model_version = Column(
        String(50),
        nullable=True,
    )

    # Training Status
    status = Column(
        String(50),
        nullable=False,
        default="QUEUED",
    )

    # Metrics
    precision = Column(
        Float,
        nullable=True,
    )

    recall = Column(
        Float,
        nullable=True,
    )

    map50 = Column(
        Float,
        nullable=True,
    )

    map50_95 = Column(
        Float,
        nullable=True,
    )

    training_time = Column(
        Float,
        nullable=True,
    )

    started_at = Column(
        DateTime,
        nullable=True,
    )

    completed_at = Column(
        DateTime,
        nullable=True,
    )

    # Relationships
    project = relationship(
        "Project",
        back_populates="training_runs",
    )

    dataset = relationship(
        "Dataset",
        back_populates="training_runs",
    )

    user = relationship(
        "User",
        back_populates="training_runs",
    )
    endpoint_name = Column(
    String(255),
    nullable=True,
)