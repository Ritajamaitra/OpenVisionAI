from xml.etree.ElementTree import Element, SubElement, tostring

from app.models.annotation import Annotation


class VOCExporter:
    """
    Builds Pascal VOC XML annotation files.
    """

    def build(
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

            root = Element("annotation")

            filename = SubElement(root, "filename")
            filename.text = image_name

            for row in rows:

                obj = SubElement(root, "object")

                name = SubElement(obj, "name")
                name.text = row.label

                bndbox = SubElement(obj, "bndbox")

                xmin = SubElement(bndbox, "xmin")
                xmin.text = str(int(row.bbox_x))

                ymin = SubElement(bndbox, "ymin")
                ymin.text = str(int(row.bbox_y))

                xmax = SubElement(bndbox, "xmax")
                xmax.text = str(
                    int(row.bbox_x + row.bbox_width)
                )

                ymax = SubElement(bndbox, "ymax")
                ymax.text = str(
                    int(row.bbox_y + row.bbox_height)
                )

            xml_name = (
                image_name.rsplit(".", 1)[0]
                + ".xml"
            )

            files[
                f"Annotations/{xml_name}"
            ] = tostring(root)

        return files