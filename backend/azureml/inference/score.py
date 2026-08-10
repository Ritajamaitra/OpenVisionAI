import json
import os

from PIL import Image
from ultralytics import YOLO


model = None


def init():
    global model

    model_dir = os.environ.get(
        "AZUREML_MODEL_DIR"
    )

    if not model_dir:
        raise RuntimeError(
            "AZUREML_MODEL_DIR is not set."
        )

    candidates = []

    for root, _, files in os.walk(model_dir):

        for filename in files:

            if filename == "best.pt":

                candidates.append(
                    os.path.join(
                        root,
                        filename,
                    )
                )

    if not candidates:

        raise FileNotFoundError(
            "best.pt was not found inside "
            "AZUREML_MODEL_DIR."
        )

    model_path = candidates[0]

    model = YOLO(model_path)


def run(raw_data):

    try:

        if isinstance(raw_data, str):

            data = json.loads(raw_data)

        else:

            data = raw_data

        image_path = data.get(
            "image_path"
        )

        if not image_path:

            raise ValueError(
                "Request must contain "
                "'image_path'."
            )

        image = Image.open(
            image_path
        )

        results = model(
            image
        )

        predictions = []

        for result in results:

            boxes = result.boxes

            for box in boxes:

                xyxy = (
                    box.xyxy[0]
                    .tolist()
                )

                confidence = float(
                    box.conf[0]
                )

                class_id = int(
                    box.cls[0]
                )

                class_name = (
                    result.names[
                        class_id
                    ]
                )

                x1, y1, x2, y2 = xyxy

                predictions.append(
                    {
                        "label": class_name,

                        "confidence": (
                            confidence
                        ),

                        "bbox": [
                            x1,
                            y1,
                            x2 - x1,
                            y2 - y1,
                        ],
                    }
                )

        return {
            "predictions": predictions
        }

    except Exception as exc:

        return {
            "error": str(exc)
        }