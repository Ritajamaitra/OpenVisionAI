from enum import Enum

class AnnotationStatus(str, Enum):
    AUTO_GENERATED = "AUTO_GENERATED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"