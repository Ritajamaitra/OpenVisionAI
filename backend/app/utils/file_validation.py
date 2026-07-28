from pathlib import Path

from fastapi import HTTPException, UploadFile, status


# ------------------------------------------------------------------
# Supported image formats
# ------------------------------------------------------------------

ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff",
    ".webp",
}


ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/bmp",
    "image/tiff",
    "image/webp",
}


# ------------------------------------------------------------------
# Supported annotation formats
# ------------------------------------------------------------------

ALLOWED_ANNOTATION_EXTENSIONS = {
    ".json",
    ".xml",
    ".txt",
}


MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


# ------------------------------------------------------------------
# Image Validation
# ------------------------------------------------------------------

def validate_image_file(
    file: UploadFile,
) -> None:
    """
    Validate an uploaded image file.
    """

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image format: {extension}",
        )

    if file.content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported content type: {file.content_type}",
        )


# ------------------------------------------------------------------
# Annotation Validation
# ------------------------------------------------------------------

def validate_annotation_file(
    file: UploadFile,
) -> None:
    """
    Validate an uploaded annotation file.
    """

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_ANNOTATION_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported annotation format: {extension}",
        )


# ------------------------------------------------------------------
# File Size Validation
# ------------------------------------------------------------------

def validate_file_size(
    file_size: int,
) -> None:
    """
    Validate uploaded file size.
    """

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Maximum allowed file size is {MAX_FILE_SIZE // (1024 * 1024)} MB.",
        )