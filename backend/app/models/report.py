from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseEntity
from app.models.report_status import ReportStatus


class Report(BaseEntity):
    __tablename__ = "reports"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False,
    )

    model_registry_id: Mapped[int] = mapped_column(
        ForeignKey("model_registry.id"),
        nullable=False,
    )

    report_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    report_uri: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus),
        nullable=False,
        default=ReportStatus.GENERATED,
    )

    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="reports",
    )

    model_registry: Mapped["ModelRegistry"] = relationship(
        "ModelRegistry",
        back_populates="reports",
    )