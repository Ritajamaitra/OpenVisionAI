from datetime import datetime
from enum import Enum

from sqlalchemy import (
    DateTime,
    Enum as SqlEnum,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseEntity


class AnnotationStatus(str, Enum):
    """
    Status of an annotation.
    """

    AUTO_GENERATED = "AUTO_GENERATED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Annotation(BaseEntity):
    """
    Stores one detected object.

    One image may have multiple annotation rows.

    Example:

    worker.jpg

        helmet
        vest
        person
        gloves
    """

    __tablename__ = "annotations"

    dataset_id: Mapped[int] = mapped_column(
        ForeignKey("datasets.id"),
        nullable=False,
    )

    image_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    label: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    bbox_x: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    bbox_y: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    bbox_width: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    bbox_height: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    status: Mapped[AnnotationStatus] = mapped_column(
        SqlEnum(AnnotationStatus),
        nullable=False,
        default=AnnotationStatus.AUTO_GENERATED,
    )

    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    reviewed_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )