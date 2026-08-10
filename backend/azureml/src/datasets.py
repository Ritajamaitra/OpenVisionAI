"""
OpenVisionAI YOLO Dataset Utilities

The Azure ML training input is a URI_FOLDER containing an
already-extracted YOLO dataset.

Expected structure:

dataset/
├── dataset.yaml
├── images/
│   └── *.png / *.jpg / ...
└── labels/
    └── *.txt
"""

from pathlib import Path
from typing import Tuple

import yaml


# ==========================================================
# Dataset Loading
# ==========================================================

def extract_dataset(dataset_path: str | Path) -> Path:
    """
    Return the mounted Azure ML dataset directory.

    The dataset is already extracted because the Azure ML
    input is registered as AssetTypes.URI_FOLDER.

    Kept under the existing function name so train.py does
    not require a larger refactor.
    """

    dataset_path = Path(dataset_path)

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset path does not exist: {dataset_path}"
        )

    if not dataset_path.is_dir():
        raise ValueError(
            f"Expected a dataset directory, got: {dataset_path}"
        )

    return dataset_path


# ==========================================================
# YAML Discovery
# ==========================================================

def _find_yaml(dataset_dir: Path) -> Path:
    """
    Find the YOLO dataset configuration file.
    """

    candidates = (
        "dataset.yaml",
        "data.yaml",
        "dataset.yml",
        "data.yml",
    )

    for name in candidates:
        yaml_path = dataset_dir / name

        if yaml_path.exists():
            return yaml_path

    raise FileNotFoundError(
        "No YOLO dataset YAML found. "
        f"Expected one of: {', '.join(candidates)} "
        f"inside {dataset_dir}"
    )


# ==========================================================
# Dataset Validation
# ==========================================================

def validate_dataset(
    dataset_dir: str | Path,
) -> Tuple[Path, dict]:
    """
    Validate the mounted YOLO dataset.

    Returns
    -------
    tuple
        (dataset_root, parsed_yaml)
    """

    dataset_dir = Path(dataset_dir)

    if not dataset_dir.exists():
        raise FileNotFoundError(
            f"Dataset directory does not exist: {dataset_dir}"
        )

    if not dataset_dir.is_dir():
        raise ValueError(
            f"Dataset root must be a directory: {dataset_dir}"
        )

    yaml_file = _find_yaml(dataset_dir)

    with yaml_file.open(
        "r",
        encoding="utf-8",
    ) as file:
        config = yaml.safe_load(file) or {}

    images_dir = dataset_dir / "images"
    labels_dir = dataset_dir / "labels"

    if not images_dir.exists():
        raise FileNotFoundError(
            f"Images directory not found: {images_dir}"
        )

    if not labels_dir.exists():
        raise FileNotFoundError(
            f"Labels directory not found: {labels_dir}"
        )

    image_files = [
        path
        for path in images_dir.rglob("*")
        if path.is_file()
        and path.suffix.lower()
        in {
            ".jpg",
            ".jpeg",
            ".png",
            ".bmp",
            ".webp",
        }
    ]

    label_files = [
        path
        for path in labels_dir.rglob("*.txt")
        if path.is_file()
    ]

    if not image_files:
        raise ValueError(
            f"No image files found in {images_dir}"
        )

    if not label_files:
        raise ValueError(
            f"No YOLO label files found in {labels_dir}"
        )

    return dataset_dir, config


# ==========================================================
# Dataset Information
# ==========================================================

def print_dataset_info(
    dataset_dir: str | Path,
    config: dict,
    logger,
) -> None:
    """
    Log useful information about the YOLO dataset.
    """

    dataset_dir = Path(dataset_dir)

    logger.info("=" * 70)
    logger.info("Dataset Information")
    logger.info("=" * 70)

    logger.info(
        "Dataset Root : %s",
        dataset_dir,
    )

    logger.info(
        "Train Path   : %s",
        config.get("train", "images"),
    )

    logger.info(
        "Val Path     : %s",
        config.get("val", config.get("train", "images")),
    )

    names = config.get("names", [])

    if isinstance(names, dict):
        names = [
            names[key]
            for key in sorted(names.keys())
        ]

    if isinstance(names, str):
        names = [names]

    nc = config.get(
        "nc",
        len(names),
    )

    logger.info(
        "Classes      : %s",
        nc,
    )

    logger.info("Class Names")

    if names:
        for index, name in enumerate(names):
            logger.info(
                "%s -> %s",
                index,
                name,
            )
    else:
        logger.info("No class names specified.")

    logger.info("=" * 70)