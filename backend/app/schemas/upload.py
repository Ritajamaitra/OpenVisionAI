from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class UploadImageResponse(BaseModel):
    """
    Response returned after uploading an image.
    """

    filename: str

    storage_path: str

    image_size: int

    content_type: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class UploadAnnotationResponse(BaseModel):
    """
    Response returned after uploading an annotation file.
    """

    filename: str

    storage_path: str

    annotation_format: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class DatasetPreviewResponse(BaseModel):
    """
    Dataset summary returned after uploads.
    """

    dataset_id: int

    total_images: int

    total_annotations: int

    storage_path: str

    dataset_version: str

    model_config = ConfigDict(
        from_attributes=True,
    )