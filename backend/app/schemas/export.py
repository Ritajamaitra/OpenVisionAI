from enum import Enum

from pydantic import BaseModel


class ExportFormat(str, Enum):
    YOLO = "yolo"
    COCO = "coco"
    VOC = "voc"


class DatasetExportResponse(BaseModel):
    dataset_id: int
    format: ExportFormat
    download_url: str