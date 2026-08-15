
import base64
import io
import json
import os

from PIL import Image
from ultralytics import YOLO


model = None


def init():
    global model

    model_dir = os.environ.get(
        "AZUREML_MODEL_DIR",
        os.environ.get("MODEL_PATH", "/app/model")
    )

    if os.path.isfile(model_dir):
        model_path = model_dir
    else:
        candidates = []

        for root, _, files in os.walk(model_dir):
            for filename in files:
                if filename == "best.pt":
                    candidates.append(
                        os.path.join(root, filename)
                    )

        if not candidates:
            raise FileNotFoundError(
                f"best.pt was not found inside {model_dir}"
            )

        model_path = candidates[0]

    print(f"Loading YOLO model from: {model_path}")

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

        confidence = float(
            data.get("confidence", 0.25)
        )

        results = model(
            image,
            conf=confidence
        )

        predictions = []

        for result in results:

            for box in result.boxes:

                xyxy = box.xyxy[0].tolist()

                confidence_value = float(
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
                    "confidence": confidence_value,
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
