"""
OpenVisionAI YOLO Trainer

Responsibilities
----------------
1. Train YOLO model
2. Resolve dataset paths explicitly for Azure ML
3. Disable Ultralytics automatic MLflow callbacks
4. Return metrics and model artifacts
"""

from pathlib import Path
from typing import Any, Dict
import os
import tempfile

import yaml

from ultralytics import YOLO, settings


# ==========================================================
# Disable Ultralytics MLflow integration
# ==========================================================

settings.update(
    {
        "mlflow": False,
    }
)

os.environ["YOLO_MLFLOW"] = "false"
os.environ["MLFLOW_TRACKING_URI"] = ""
os.environ["MLFLOW_ENABLE_SYSTEM_METRICS_LOGGING"] = "false"


# ==========================================================
# Dataset YAML Resolution
# ==========================================================

def _resolve_dataset_yaml(
    dataset_yaml: str | Path,
) -> Path:
    """
    Create an Azure-ML-safe YOLO dataset YAML.

    The exported YAML contains relative paths such as:

        path: ./
        train: images
        val: images

    Ultralytics can resolve these incorrectly inside Azure ML.

    This function converts train/val paths into absolute paths
    based on the actual extracted dataset directory.
    """

    dataset_yaml = Path(dataset_yaml).resolve()

    if not dataset_yaml.exists():
        raise FileNotFoundError(
            f"Dataset YAML does not exist: {dataset_yaml}"
        )

    dataset_root = dataset_yaml.parent

    with dataset_yaml.open(
        "r",
        encoding="utf-8",
    ) as file:
        config = yaml.safe_load(file) or {}

    # ------------------------------------------------------
    # Resolve train path
    # ------------------------------------------------------

    train_value = config.get(
        "train",
        "images",
    )

    train_path = Path(
        str(train_value)
    )

    if not train_path.is_absolute():

        train_path = (
            dataset_root / train_path
        ).resolve()

    # ------------------------------------------------------
    # Resolve validation path
    # ------------------------------------------------------

    val_value = config.get(
        "val",
        train_value,
    )

    val_path = Path(
        str(val_value)
    )

    if not val_path.is_absolute():

        val_path = (
            dataset_root / val_path
        ).resolve()

    # ------------------------------------------------------
    # Validate directories
    # ------------------------------------------------------

    if not train_path.exists():
        raise FileNotFoundError(
            f"YOLO training images directory does not exist: "
            f"{train_path}"
        )

    if not train_path.is_dir():
        raise ValueError(
            f"YOLO training path is not a directory: "
            f"{train_path}"
        )

    if not val_path.exists():
        raise FileNotFoundError(
            f"YOLO validation images directory does not exist: "
            f"{val_path}"
        )

    if not val_path.is_dir():
        raise ValueError(
            f"YOLO validation path is not a directory: "
            f"{val_path}"
        )

    # ------------------------------------------------------
    # Replace with absolute paths
    # ------------------------------------------------------

    config["path"] = str(
        dataset_root
    )

    config["train"] = str(
        train_path
    )

    config["val"] = str(
        val_path
    )

    # ------------------------------------------------------
    # Write resolved YAML
    # ------------------------------------------------------

    resolved_yaml = (
        dataset_root
        / "dataset_resolved.yaml"
    )

    with resolved_yaml.open(
        "w",
        encoding="utf-8",
    ) as file:

        yaml.safe_dump(
            config,
            file,
            sort_keys=False,
        )

    return resolved_yaml


# ==========================================================
# Train Model
# ==========================================================

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

    # ------------------------------------------------------
    # Resolve dataset paths
    # ------------------------------------------------------

    resolved_yaml = _resolve_dataset_yaml(
        dataset_yaml
    )

    print("=" * 70)
    print("Resolved YOLO Dataset")
    print("=" * 70)

    print(
        "Original YAML :",
        Path(dataset_yaml).resolve(),
    )

    print(
        "Resolved YAML :",
        resolved_yaml,
    )

    # ------------------------------------------------------
    # Load model
    # ------------------------------------------------------

    model = YOLO(
        model_name
    )

    # ------------------------------------------------------
    # Training
    # ------------------------------------------------------

    print("=" * 70)
    print("Starting YOLO Training")
    print("=" * 70)

    results = model.train(
        data=str(
            resolved_yaml
        ),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        project=project,
        name=experiment,
        device=device,
        exist_ok=True,
        verbose=True,
    )

    # ------------------------------------------------------
    # Outputs
    # ------------------------------------------------------

    save_dir = Path(
        results.save_dir
    )

    best_model = (
        save_dir
        / "weights"
        / "best.pt"
    )

    last_model = (
        save_dir
        / "weights"
        / "last.pt"
    )

    # ------------------------------------------------------
    # Metrics
    # ------------------------------------------------------

    metrics = {}

    if hasattr(
        results,
        "results_dict",
    ):

        metrics = dict(
            results.results_dict
        )

    # ------------------------------------------------------
    # Logging
    # ------------------------------------------------------

    print("=" * 70)
    print("Training finished")
    print("=" * 70)

    print(
        "Best model :",
        best_model,
    )

    print(
        "Last model :",
        last_model,
    )

    print(
        "Save dir   :",
        save_dir,
    )

    print("=" * 70)

    return {
        "best_model": str(
            best_model
        ),
        "last_model": str(
            last_model
        ),
        "save_dir": str(
            save_dir
        ),
        "metrics": metrics,
    }