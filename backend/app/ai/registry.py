from dataclasses import dataclass

from app.ai.detectors.grounding_dino import GroundingDINODetector


@dataclass(frozen=True)
class VisionModel:

    name: str

    display_name: str

    task: str

    detector: type

    supports_zero_shot: bool


VISION_MODELS = {

    "grounding_dino": VisionModel(

        name="grounding_dino",

        display_name="Grounding DINO",

        task="object_detection",

        detector=GroundingDINODetector,

        supports_zero_shot=True,
    ),
}