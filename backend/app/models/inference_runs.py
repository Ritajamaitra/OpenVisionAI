from sqlalchemy import Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import ModelRegistry, User
from app.models.base import BaseEntity


class InferenceRun(BaseEntity):
    __tablename__ = "inference_runs"

    model_registry_id: Mapped[int] = mapped_column(
        ForeignKey("model_registry.id"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    model_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    confidence_threshold: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    prediction_count: Mapped[int] = mapped_column(
    Integer,
    nullable=False,
    default=0,
    server_default="0",
)

    predictions_json: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    inference_latency_ms: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    input_filename: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    input_content_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )

    model_registry: Mapped["ModelRegistry"] = relationship(
        "ModelRegistry",
    )

    user: Mapped["User"] = relationship(
        "User",
    )