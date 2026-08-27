"""Models package exports and registration for Alembic."""

from app.models.base import BaseEntity
from app.models.model_registry import ModelRegistry
from app.models.dataset import Dataset
from app.models.project import Project
from app.models.report import Report
from app.models.user import User
from app.models.annotation import Annotation
from app.models.training_run import TrainingRun

__all__ = [
    "BaseEntity",
    "User",
    "Project",
    "Dataset",
    "ModelRegistry",
    "Report",
    "Annotation",
    "TrainingRun",
]
