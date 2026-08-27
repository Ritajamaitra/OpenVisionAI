import base64
import io
import os

from fastapi import FastAPI
from pydantic import BaseModel
from PIL import Image
from ultralytics import YOLO


MODEL_PATH = os.getenv(
    "OPENVISIONAI_MODEL_PATH",
    r".\models\openvisionai-yolo-v2\openvisionai-yolo\best.pt",
)

app = FastAPI(title="OpenVisionAI Inference Service")

model = YOLO(MODEL_PATH)


class ScoreRequest(BaseModel):
    image_base64: str
    confidence: float = 0.25


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model": MODEL_PATH,
    }


@app.post("/score")
def score(request: ScoreRequest):

    try:
        image_bytes = base64.b64decode(request.image_base64)

        image = Image.open(
            io.BytesIO(image_bytes)
        ).convert("RGB")

        results = model.predict(
            source=image,
            conf=request.confidence,
            verbose=False,
        )

        predictions = []

        for result in results:

            boxes = result.boxes

            if boxes is None:
                continue

            for box in boxes:

                cls_id = int(
                    box.cls[0].item()
                )

                confidence = float(
                    box.conf[0].item()
                )

                xyxy = (
                    box.xyxy[0]
                    .tolist()
                )

                class_name = (
                    result.names.get(
                        cls_id,
                        str(cls_id),
                    )
                )

                predictions.append(
                    {
                        "class": class_name,
                        "class_id": cls_id,
                        "confidence": confidence,
                        "bbox": xyxy,
                    }
                )

        return {
            "predictions": predictions
        }

    except Exception as exc:

        return {
            "error": str(exc)
        }