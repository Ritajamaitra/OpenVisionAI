import base64
import io
import json
import os

from PIL import Image
from ultralytics import YOLO


model = None


def init():
    global model

    model_path = os.environ.get(
        "MODEL_PATH",
        "/app/model/best.pt"
    )

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model not found: {model_path}"
        )

    model = YOLO(model_path)


def run(raw_data):

    try:
        if isinstance(raw_data, str):
            data = json.loads(raw_data)
        else:
            data = raw_data

        image_base64 = data.get("image_base64")

        if not image_base64:
            raise ValueError(
                "Request must contain 'image_base64'."
            )

        if "," in image_base64:
            image_base64 = image_base64.split(",", 1)[1]

        image_bytes = base64.b64decode(image_base64)

        image = Image.open(
            io.BytesIO(image_bytes)
        ).convert("RGB")

        results = model(
            image,
            conf=float(data.get("confidence", 0.25))
        )

        predictions = []

        for result in results:

            for box in result.boxes:

                xyxy = box.xyxy[0].tolist()

                confidence = float(
                    box.conf[0]
                )

                class_id = int(
                    box.cls[0]
                )

                class_name = result.names[
                    class_id
                ]

                x1, y1, x2, y2 = xyxy

                predictions.append({
                    "label": class_name,
                    "confidence": confidence,
                    "bbox": [
                        x1,
                        y1,
                        x2 - x1,
                        y2 - y1
                    ]
                })

        return {
            "predictions": predictions
        }

    except Exception as exc:

        return {
            "error": str(exc)
        }
