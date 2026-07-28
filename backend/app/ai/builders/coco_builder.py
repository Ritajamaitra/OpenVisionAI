from collections import OrderedDict
from datetime import datetime
import json
from pathlib import Path


class COCOBuilder:
    """
    Converts OpenVisionAI detections into COCO format.
    """

    def build(
        self,
        image_name: str,
        width: int,
        height: int,
        detections: list[dict],
    ) -> dict:

        categories = OrderedDict()

        annotations = []

        annotation_id = 1

        for detection in detections:

            label = detection["label"]

            if label not in categories:
                categories[label] = len(categories) + 1

            category_id = categories[label]

            x, y, w, h = detection["bbox"]

            annotations.append(
                {
                    "id": annotation_id,
                    "image_id": 1,
                    "category_id": category_id,
                    "bbox": [
                        round(x, 2),
                        round(y, 2),
                        round(w, 2),
                        round(h, 2),
                    ],
                    "area": round(w * h, 2),
                    "iscrowd": 0,
                    "score": round(
                        detection["confidence"],
                        4,
                    ),
                }
            )

            annotation_id += 1

        coco = {

            "info": {
                "description": "OpenVisionAI Auto Annotation",
                "version": "1.0",
                "date_created": datetime.utcnow().isoformat(),
            },

            "images": [

                {
                    "id": 1,
                    "file_name": image_name,
                    "width": width,
                    "height": height,
                }

            ],

            "categories": [

                {
                    "id": category_id,
                    "name": label,
                    "supercategory": "object",
                }

                for label, category_id in categories.items()

            ],

            "annotations": annotations,
        }

        return coco

    def save(self, coco_dict: dict, output_path: str | Path) -> None:
        """
        Save a COCO-format dictionary to a JSON file at `output_path`.

        Args:
            coco_dict: The COCO-format dictionary returned by `build()`.
            output_path: Path to write the JSON file to. Parent directories
                         will be created if they do not exist.
        """
        path = Path(output_path)
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as fh:
            json.dump(coco_dict, fh, ensure_ascii=False, indent=2)