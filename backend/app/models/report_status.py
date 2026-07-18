from enum import Enum


class ReportStatus(str, Enum):
    GENERATED = "GENERATED"
    PENDING = "PENDING"
    FAILED = "FAILED"