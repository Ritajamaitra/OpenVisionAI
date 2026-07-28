from abc import ABC, abstractmethod
from typing import Any


class BaseDetector(ABC):
    """
    Base interface for every vision model.

    Every detector must return detections in a
    common format regardless of the underlying model.
    """

    @abstractmethod
    def predict(
        self,
        image: Any,
        confidence: float = 0.35,
    ) -> list[dict]:
        """
        Returns

        [
            {
                "bbox": [x, y, width, height],
                "label": "helmet",
                "confidence": 0.94,
            }
        ]
        """
        raise NotImplementedError