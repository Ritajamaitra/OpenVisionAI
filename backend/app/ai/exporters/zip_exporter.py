from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile


class ZipExporter:
    """
    Creates an in-memory ZIP archive for dataset exports.

    Example output:

    dataset.zip
    ├── images/
    │   ├── 1.jpg
    │   ├── 2.jpg
    │   └── ...
    ├── labels/
    │   ├── 1.txt
    │   └── 2.txt
    ├── annotations.json
    └── dataset.yaml
    """

    def create_zip(
        self,
        images: dict[str, bytes],
        export_files: dict[str, bytes],
    ) -> bytes:
        """
        Parameters
        ----------
        images
            Dictionary of image blob paths to image bytes.

            Example:
            {
                "datasets/project_1/dataset_4/images/1.jpg": b"...",
                "datasets/project_1/dataset_4/images/2.jpg": b"..."
            }

        export_files
            Dictionary containing generated export files.

            Example (YOLO):
            {
                "labels/1.txt": b"...",
                "labels/2.txt": b"...",
                "dataset.yaml": b"..."
            }

            Example (COCO):
            {
                "annotations.json": b"..."
            }

            Example (VOC):
            {
                "Annotations/1.xml": b"...",
                "Annotations/2.xml": b"..."
            }

        Returns
        -------
        bytes
            ZIP archive as bytes.
        """

        buffer = BytesIO()

        with ZipFile(
            buffer,
            mode="w",
            compression=ZIP_DEFLATED,
        ) as zip_file:

            # -----------------------------
            # Add images
            # -----------------------------
            for blob_path, image_bytes in images.items():

                image_name = blob_path.split("/")[-1]

                zip_file.writestr(
                    f"images/{image_name}",
                    image_bytes,
                )

            # -----------------------------
            # Add export files
            # -----------------------------
            for filename, file_bytes in export_files.items():

                zip_file.writestr(
                    filename,
                    file_bytes,
                )

        buffer.seek(0)

        return buffer.read()