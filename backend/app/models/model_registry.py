from sqlalchemy import Enum, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseEntity
from app.models.model_status import ModelStatus

class ModelRegistry(BaseEntity):
    __tablename__ = "model_registry"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    dataset_id: Mapped[int] = mapped_column(
        ForeignKey("datasets.id"),
        nullable=False,
    )

    model_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    framework: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    mlflow_run_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    artifact_uri: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    metrics_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    status: Mapped[ModelStatus] = mapped_column(
        Enum(ModelStatus),
        nullable=False,
        default=ModelStatus.ACTIVE,
    )

    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        back_populates="models",
    )

    reports: Mapped[list["Report"]] = relationship(
        "Report",
        back_populates="model_registry",
    )