from pydantic import BaseModel, Field


class InferenceRequest(BaseModel):
    image_base64: str = Field(
        ...,
        description="Base64 encoded image"
    )

    confidence: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
        description="YOLO confidence threshold"
    )




class InferenceResponse(BaseModel):
    inference_id: int
    model_id: int
    model_name: str
    model_version: str
    predictions: list[dict]