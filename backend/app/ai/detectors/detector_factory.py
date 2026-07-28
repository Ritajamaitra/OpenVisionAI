from app.ai.registry import VISION_MODELS


class DetectorFactory:

    @staticmethod
    def get_detector(model_name: str):

        if model_name not in VISION_MODELS:
            raise ValueError(
                f"Unsupported model: {model_name}"
            )

        return VISION_MODELS[
            model_name
        ].detector()