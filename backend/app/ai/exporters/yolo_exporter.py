from collections import OrderedDict
from io import BytesIO

from PIL import Image

from app.models.annotation import Annotation


class YOLOExporter:
    """
    Converts reviewed annotations into a YOLO training dataset.

    Database annotations are stored as pixel coordinates:

        bbox_x
        bbox_y
        bbox_width
        bbox_height

    YOLO requires normalized coordinates:

        x_center
        y_center
        width
        height

    where every value is in the range [0, 1].
    """

    def build_labels(
        self,
        annotations: list[Annotation],
        images: dict[str, bytes] | None = None,
    ) -> dict[str, bytes]:

        files: dict[str, bytes] = {}

        if images is None:
            raise ValueError(
                "Image data is required for YOLO export "
                "because bounding boxes are stored in pixel coordinates."
            )

        # ---------------------------------------------------------
        # 1. Keep only approved annotations
        # ---------------------------------------------------------

        approved = [
            annotation
            for annotation in annotations
            if annotation.status.value == "APPROVED"
        ]

        if not approved:
            raise ValueError(
                "No approved annotations available for training."
            )

        # ---------------------------------------------------------
        # 2. Build deterministic class mapping
        # ---------------------------------------------------------

        class_names = sorted(
            {
                annotation.label.strip()
                for annotation in approved
                if annotation.label
                and annotation.label.strip()
            }
        )

        if not class_names:
            raise ValueError(
                "No valid annotation classes found."
            )

        class_to_id = {
            class_name: index
            for index, class_name in enumerate(class_names)
        }

        # ---------------------------------------------------------
        # 3. Group annotations by image
        # ---------------------------------------------------------

        grouped: dict[str, list[Annotation]] = {}

        for annotation in approved:
            grouped.setdefault(
                annotation.image_name,
                [],
            ).append(annotation)

        # ---------------------------------------------------------
        # 4. Build image lookup
        #
        # Blob storage returns full blob paths:
        #
        # datasets/project_1/dataset_4/images/1.jpg
        #
        # Annotation.image_name contains:
        #
        # 1.jpg
        #
        # So match using the filename.
        # ---------------------------------------------------------

        image_lookup: dict[str, bytes] = {}

        for blob_path, image_bytes in images.items():
            filename = blob_path.split("/")[-1]

            image_lookup[filename] = image_bytes

        # ---------------------------------------------------------
        # 5. Generate YOLO label files
        # ---------------------------------------------------------

        for image_name, rows in grouped.items():

            image_bytes = image_lookup.get(
                image_name
            )

            if image_bytes is None:
                raise ValueError(
                    f"Image '{image_name}' was not found "
                    "in the exported dataset."
                )

            # -----------------------------------------------------
            # Read image dimensions
            # -----------------------------------------------------

            try:
                with Image.open(
                    BytesIO(image_bytes)
                ) as image:

                    image_width, image_height = image.size

            except Exception as exc:

                raise ValueError(
                    f"Could not read image dimensions for "
                    f"'{image_name}': {exc}"
                ) from exc

            if image_width <= 0 or image_height <= 0:
                raise ValueError(
                    f"Invalid image dimensions for "
                    f"'{image_name}': "
                    f"{image_width}x{image_height}"
                )

            lines: list[str] = []

            # -----------------------------------------------------
            # Convert each pixel bbox to YOLO format
            # -----------------------------------------------------

            for row in rows:

                label = (
                    row.label.strip()
                    if row.label
                    else None
                )

                if not label:
                    continue

                class_id = class_to_id[label]

                # ---------------------------------------------------------
                # Database bbox is stored in pixel coordinates:
                #
                # x      = left
                # y      = top
                # width  = width
                # height = height
                #
                # Clip the bbox to the actual image boundaries.
                # ---------------------------------------------------------

                x = float(row.bbox_x)
                y = float(row.bbox_y)
                width = float(row.bbox_width)
                height = float(row.bbox_height)

                if width <= 0 or height <= 0:
                    raise ValueError(
                        f"Invalid bounding box dimensions for "
                        f"{image_name}: "
                        f"x={x}, y={y}, "
                        f"width={width}, height={height}"
                    )

                # Original bottom-right coordinates
                x2 = x + width
                y2 = y + height

                # Clip to image boundaries
                x1_clipped = max(0.0, x)
                y1_clipped = max(0.0, y)

                x2_clipped = min(
                    float(image_width),
                    x2,
                )

                y2_clipped = min(
                    float(image_height),
                    y2,
                )

                # Make sure the clipped box is still valid
                if x2_clipped <= x1_clipped:
                    raise ValueError(
                        f"Bounding box has no valid width after clipping "
                        f"for {image_name}: "
                        f"{x}, {y}, {width}, {height}"
                    )

                if y2_clipped <= y1_clipped:
                    raise ValueError(
                        f"Bounding box has no valid height after clipping "
                        f"for {image_name}: "
                        f"{x}, {y}, {width}, {height}"
                    )

                # ---------------------------------------------------------
                # Convert clipped pixel bbox to YOLO format
                # ---------------------------------------------------------

                clipped_width = (
                    x2_clipped - x1_clipped
                )

                clipped_height = (
                    y2_clipped - y1_clipped
                )

                x_center = (
                    x1_clipped
                    + clipped_width / 2
                ) / image_width

                y_center = (
                    y1_clipped
                    + clipped_height / 2
                ) / image_height

                normalized_width = (
                    clipped_width / image_width
                )

                normalized_height = (
                    clipped_height / image_height
                )

                # -------------------------------------------------
                # Final YOLO validation
                # -------------------------------------------------

                values = [
                    x_center,
                    y_center,
                    normalized_width,
                    normalized_height,
                ]

                if not all(
                    0.0 <= value <= 1.0
                    for value in values
                ):
                    raise ValueError(
                        f"Invalid normalized YOLO bounding box "
                        f"for {image_name}: {values}"
                    )

                lines.append(
                    f"{class_id} "
                    f"{x_center:.6f} "
                    f"{y_center:.6f} "
                    f"{normalized_width:.6f} "
                    f"{normalized_height:.6f}"
                )

            # -----------------------------------------------------
            # Generate label file
            # -----------------------------------------------------

            if not lines:
                continue

            label_name = (
                image_name.rsplit(".", 1)[0]
                + ".txt"
            )

            files[
                f"labels/{label_name}"
            ] = (
                "\n".join(lines)
                + "\n"
            ).encode("utf-8")

        # ---------------------------------------------------------
        # 6. Generate dataset.yaml
        # ---------------------------------------------------------

        yaml_lines = [
            "path: ./",
            "train: images",
            "val: images",
            f"nc: {len(class_names)}",
            "names:",
        ]

        for index, class_name in enumerate(class_names):

            safe_name = class_name.replace(
                '"',
                "'",
            )

            yaml_lines.append(
                f'  {index}: "{safe_name}"'
            )

        files["dataset.yaml"] = (
            "\n".join(yaml_lines)
            + "\n"
        ).encode("utf-8")

        return files