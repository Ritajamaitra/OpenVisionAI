from app.models.annotation import Annotation


class YOLOExporter:
    """
    Converts approved annotations into YOLO label files.
    """

    def build_labels(
        self,
        annotations: list[Annotation],
    ) -> dict[str, bytes]:

        files = {}

        grouped = {}

        for annotation in annotations:

            grouped.setdefault(
                annotation.image_name,
                [],
            ).append(annotation)

        for image_name, rows in grouped.items():

            lines = []

            for row in rows:

                # Placeholder class id.
                class_id = 0

                x_center = row.bbox_x
                y_center = row.bbox_y
                width = row.bbox_width
                height = row.bbox_height

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
            "path: ./\n"
            "train: images\n"
            "val: images\n"
            "nc: 1\n"
            "names:\n"
            "  0: object\n"
        )

        files["dataset.yaml"] = yaml.encode("utf-8")

        return files