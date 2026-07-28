import json

from app.models.annotation import Annotation


class COCOExporter:
    """
    Builds a COCO annotations.json file from approved annotations.
    """

    def build(
        self,
        annotations: list[Annotation],
    ) -> bytes:

        images = []
        categories = []
        coco_annotations = []

        image_ids = {}
        category_ids = {}

        next_image_id = 1
        next_category_id = 1
        next_annotation_id = 1

        for annotation in annotations:

            # -----------------------
            # Images
            # -----------------------

            if annotation.image_name not in image_ids:

                image_ids[annotation.image_name] = next_image_id

                images.append(
                    {
                        "id": next_image_id,
                        "file_name": annotation.image_name,
                    }
                )

                next_image_id += 1

            # -----------------------
            # Categories
            # -----------------------

            if annotation.label not in category_ids:

                category_ids[annotation.label] = next_category_id

                categories.append(
                    {
                        "id": next_category_id,
                        "name": annotation.label,
                    }
                )

                next_category_id += 1

            # -----------------------
            # Annotation
            # -----------------------

            coco_annotations.append(
                {
                    "id": next_annotation_id,
                    "image_id": image_ids[
                        annotation.image_name
                    ],
                    "category_id": category_ids[
                        annotation.label
                    ],
                    "bbox": [
                        annotation.bbox_x,
                        annotation.bbox_y,
                        annotation.bbox_width,
                        annotation.bbox_height,
                    ],
                    "area": (
                        annotation.bbox_width
                        * annotation.bbox_height
                    ),
                    "iscrowd": 0,
                }
            )

            next_annotation_id += 1

        coco = {
            "images": images,
            "categories": categories,
            "annotations": coco_annotations,
        }

        return json.dumps(
            coco,
            indent=2,
        ).encode("utf-8")