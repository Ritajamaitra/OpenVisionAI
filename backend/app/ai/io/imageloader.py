from io import BytesIO

from PIL import Image


class ImageLoader:

    @staticmethod
    def load(
        image_bytes: bytes,
    ) -> Image.Image:

        image = Image.open(
            BytesIO(image_bytes)
        )

        return image.convert("RGB")