from datetime import datetime
from typing import List

from pydantic import (
    BaseModel,
    ConfigDict,
)

from app.models.annotation import AnnotationStatus


class AutoAnnotationRequest(BaseModel):
    """
    Request body for auto-annotation endpoint.
    """

    model: str

    prompt: str

    confidence: float

    model_config = ConfigDict(
        from_attributes=True,
    )


class AutoAnnotationResponse(BaseModel):
    """
    Response returned after running auto-annotation.
    """

    image_name: str

    model: str

    detections: int

    classes: List[str]

    annotation_uri: str

    processing_time_ms: float

    model_config = ConfigDict(
        from_attributes=True,
    )


class AnnotationReview(BaseModel):
    """
    Human review request.
    """

    status: AnnotationStatus


class AnnotationResponse(BaseModel):
    """
    Single annotation returned by the API.
    """

    id: int

    dataset_id: int

    image_name: str

    label: str

    confidence: float

    bbox_x: float

    bbox_y: float

    bbox_width: float

    bbox_height: float

    status: AnnotationStatus

    reviewed_at: datetime | None = None

    reviewed_by: int | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )




class AnnotationListResponse(BaseModel):
    """
    Response returned when listing annotations.
    """

    annotations: list[AnnotationResponse]

    total: int

    model_config = ConfigDict(
        from_attributes=True,
    )