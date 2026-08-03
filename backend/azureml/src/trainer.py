"""
OpenVisionAI YOLO Trainer

Responsibilities
----------------
1. Train YOLO model
2. Disable Ultralytics automatic MLflow callbacks
3. Return metrics to train.py
"""

from pathlib import Path
from typing import Any, Dict
import os

from ultralytics import YOLO, settings


# ---------------------------------------------------------
# Disable Ultralytics MLflow integration
# ---------------------------------------------------------

settings.update(
    {
        "mlflow": False,
    }
)

os.environ["YOLO_MLFLOW"] = "false"
os.environ["MLFLOW_TRACKING_URI"] = ""
os.environ["MLFLOW_ENABLE_SYSTEM_METRICS_LOGGING"] = "false"


# ---------------------------------------------------------
# Train Model
# ---------------------------------------------------------

def train_model(
    dataset_yaml: str | Path,
    model_name: str,
    epochs: int,
    imgsz: int,
    batch: int,
    project: str,
    experiment: str,
    device: str = "cpu",
) -> Dict[str, Any]:

    print("=" * 70)
    print("Loading YOLO model")
    print("=" * 70)

    model = YOLO(model_name)

    print("=" * 70)
    print("Starting training")
    print("=" * 70)

    results = model.train(
        data=str(dataset_yaml),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        project=project,
        name=experiment,
        device=device,
        exist_ok=True,
        verbose=True,
    )

    save_dir = Path(results.save_dir)

    best_model = save_dir / "weights" / "best.pt"
    last_model = save_dir / "weights" / "last.pt"

    metrics = {}

    if hasattr(results, "results_dict"):
        metrics = dict(results.results_dict)

    print("=" * 70)
    print("Training finished")
    print("=" * 70)

    print("Best model :", best_model)
    print("Last model :", last_model)

    print("=" * 70)

    return {
        "best_model": str(best_model),
        "last_model": str(last_model),
        "save_dir": str(save_dir),
        "metrics": metrics,
    }