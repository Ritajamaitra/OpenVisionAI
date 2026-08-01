"""
YOLO trainer for OpenVisionAI.
"""

from pathlib import Path
from typing import Dict, Any

from ultralytics import YOLO


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
    """
    Train a YOLO model.

    Parameters
    ----------
    dataset_yaml : str | Path
        Path to dataset.yaml or data.yaml.

    model_name : str
        YOLO model checkpoint (e.g. yolov8n.pt)

    epochs : int

    imgsz : int

    batch : int

    project : str
        Output directory.

    experiment : str
        Run name.

    device : str
        cpu / cuda

    Returns
    -------
    dict
    """

    model = YOLO(model_name)

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
        metrics = results.results_dict

    return {
        "best_model": str(best_model),
        "last_model": str(last_model),
        "save_dir": str(save_dir),
        "metrics": metrics,
    }