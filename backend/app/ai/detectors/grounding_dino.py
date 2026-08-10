import torch
from PIL import Image
from transformers import (
    AutoModelForZeroShotObjectDetection,
    AutoProcessor,
)

from app.ai.detectors.base_detector import BaseDetector
from app.config.settings import settings
from huggingface_hub import login

class GroundingDINODetector(BaseDetector):
    """
    Grounding DINO implementation.
    """

    _model = None
    _processor = None

    def __init__(self):
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        self.model, self.processor = self.load_model()

        if settings.hf_token is not None:
            login(token=settings.hf_token)

    def load_model(self):

        if (
            GroundingDINODetector._model is None
            or GroundingDINODetector._processor is None
        ):

            GroundingDINODetector._processor = (
                AutoProcessor.from_pretrained(
                    "IDEA-Research/grounding-dino-base"
                )
            )

            GroundingDINODetector._model = (
                AutoModelForZeroShotObjectDetection.from_pretrained(
                    "IDEA-Research/grounding-dino-base"
                )
            )

            GroundingDINODetector._model.to(self.device)
            GroundingDINODetector._model.eval()

        return (
            GroundingDINODetector._model,
            GroundingDINODetector._processor,
        )

    def predict(
        self,
        image: Image.Image,
        prompt: str,
        confidence: float = 0.35,
    ) -> list[dict]:

        if image.mode != "RGB":
            image = image.convert("RGB")

        inputs = self.processor(
            images=image,
            text=prompt,
            return_tensors="pt",
        )

        inputs = {
            k: v.to(self.device)
            for k, v in inputs.items()
        }

        with torch.no_grad():
            outputs = self.model(**inputs)

        results = (
            self.processor.post_process_grounded_object_detection(
                outputs=outputs,
                input_ids=inputs["input_ids"],
                threshold=confidence,
                text_threshold=0.25,
                target_sizes=[image.size[::-1]],
            )
        )

        detections = []

        result = results[0]

        for box, score, label in zip(
            result["boxes"],
            result["scores"],
            result["labels"],
        ):

            x1, y1, x2, y2 = box.tolist()

            detections.append(
                {
                    "bbox": [
                        float(x1),
                        float(y1),
                        float(x2 - x1),
                        float(y2 - y1),
                    ],
                    "label": str(label),
                    "confidence": float(score),
                }
            )

        return detections