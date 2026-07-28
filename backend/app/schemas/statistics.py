from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DatasetStatisticsResponse(BaseModel):

    dataset_id: int

    total_images: int

    annotated_images: int

    total_annotations: int

    total_classes: int

    last_updated: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )