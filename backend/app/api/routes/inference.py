import base64

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.inference import (
    InferenceResponse,
)
from app.services.inference_services import (
    InferenceException,
    InferenceService,
)


router = APIRouter(
    tags=["Inference"],
)


@router.post(
    "/models/{model_id}/infer",
    response_model=InferenceResponse,
)
async def infer_model(
    model_id: int,
    image: UploadFile = File(
        ...,
        description="Image to run inference on",
    ),
    confidence: float = Form(
        default=0.25,
        ge=0.0,
        le=1.0,
        description="YOLO confidence threshold",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    # ---------------------------------------------
    # 1. Validate uploaded file
    # ---------------------------------------------

    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must be an image.",
        )

    # ---------------------------------------------
    # 2. Read image bytes
    # ---------------------------------------------

    try:
        image_bytes = await image.read()

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not read uploaded image: {exc}",
        )

    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded image is empty.",
        )

    # ---------------------------------------------
    # 3. Convert image → Base64
    # ---------------------------------------------

    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    # ---------------------------------------------
    # 4. Execute inference
    # ---------------------------------------------

    service = InferenceService(db)

    try:

        return service.infer(
            model_id=model_id,
            image_base64=image_base64,
            confidence=confidence,
            current_user=current_user,
        )

    except PermissionError as exc:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )

    except InferenceException as exc:

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )