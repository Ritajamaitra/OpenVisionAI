from io import BytesIO

from PIL import Image

from app.models.annotation import Annotation


class YOLOExporter:
    """
    Export annotations in YOLO format.

    Database stores:

        bbox_x      = x_min
        bbox_y      = y_min
        bbox_width  = width
        bbox_height = height

    YOLO requires:

        class_id
        x_center
        y_center
        width
        height

    where all coordinates are normalized to [0, 1].
    """

    def build_labels(
        self,
        annotations: list[Annotation],
        images: dict[str, bytes],
    ) -> dict[str, bytes]:

        files: dict[str, bytes] = {}

        grouped: dict[str, list[Annotation]] = {}

        for annotation in annotations:
            grouped.setdefault(
                annotation.image_name,
                [],
            ).append(annotation)

        for image_name, rows in grouped.items():

            if image_name not in images:
                print(
                    f"WARNING: Image '{image_name}' not found. "
                    "Skipping label generation."
                )
                continue

            image = Image.open(
                BytesIO(images[image_name])
            )

            image_width, image_height = image.size

            if image_width <= 0 or image_height <= 0:
                print(
                    f"WARNING: Invalid image size for {image_name}"
                )
                continue

            lines: list[str] = []

            for row in rows:

                class_id = 0

                x_min = float(row.bbox_x)
                y_min = float(row.bbox_y)
                width = float(row.bbox_width)
                height = float(row.bbox_height)

                if width <= 0 or height <= 0:
                    continue

                x_center = x_min + (width / 2.0)
                y_center = y_min + (height / 2.0)

                x_center /= image_width
                y_center /= image_height
                width /= image_width
                height /= image_height

                # Clamp values to YOLO limits
                x_center = min(max(x_center, 0.0), 1.0)
                y_center = min(max(y_center, 0.0), 1.0)
                width = min(max(width, 0.0), 1.0)
                height = min(max(height, 0.0), 1.0)

                if (
                    width <= 0
                    or height <= 0
                ):
                    continue

                lines.append(
                    f"{class_id} "
                    f"{x_center:.6f} "
                    f"{y_center:.6f} "
                    f"{width:.6f} "
                    f"{height:.6f}"
                )

            label_name = (
                image_name.rsplit(".", 1)[0]
                + ".txt"
            )

            files[
                f"labels/{label_name}"
            ] = "\n".join(lines).encode("utf-8")

        yaml = (
            "train: images\n"
            "val: images\n"
            "nc: 1\n"
            "names:\n"
            "  0: object\n"
        )

        files["dataset.yaml"] = yaml.encode(
            "utf-8"
        )

        return files