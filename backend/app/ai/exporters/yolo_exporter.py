from collections import OrderedDict

from app.models.annotation import Annotation


class YOLOExporter:
    """
    Converts reviewed annotations into a YOLO training dataset.

    The exporter:
    - groups annotations by image
    - creates a deterministic class mapping
    - generates YOLO .txt label files
    - generates dataset.yaml
    """

    def build_labels(
        self,
        annotations: list[Annotation],
        images=None,
    ) -> dict[str, bytes]:

        files: dict[str, bytes] = {}

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
        # 4. Generate YOLO label files
        # ---------------------------------------------------------

        for image_name, rows in grouped.items():

            lines: list[str] = []

            for row in rows:

                label = (
                    row.label.strip()
                    if row.label
                    else None
                )

                if not label:
                    continue

                class_id = class_to_id[label]

                x_center = float(row.bbox_x)
                y_center = float(row.bbox_y)
                width = float(row.bbox_width)
                height = float(row.bbox_height)

                # -------------------------------------------------
                # Validate normalized coordinates
                # -------------------------------------------------

                values = [
                    x_center,
                    y_center,
                    width,
                    height,
                ]

                if not all(
                    0.0 <= value <= 1.0
                    for value in values
                ):
                    raise ValueError(
                        f"Invalid YOLO bounding box for "
                        f"{image_name}: {values}"
                    )

                lines.append(
                    f"{class_id} "
                    f"{x_center:.6f} "
                    f"{y_center:.6f} "
                    f"{width:.6f} "
                    f"{height:.6f}"
                )

            if not lines:
                continue

            label_name = (
                image_name.rsplit(".", 1)[0]
                + ".txt"
            )

            files[
                f"labels/{label_name}"
            ] = "\n".join(lines).encode("utf-8")

        # ---------------------------------------------------------
        # 5. Generate dataset.yaml
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
            "\n".join(yaml_lines) + "\n"
        ).encode("utf-8")

        return files