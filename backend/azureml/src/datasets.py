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
    Resolve an Azure ML dataset input.

    Supports:
    1. Already-mounted YOLO dataset directory
    2. ZIP dataset supplied as a file

    Returns
    -------
    Path
        Directory containing dataset.yaml/data.yaml,
        images/, and labels/.
    """

    import shutil
    import tempfile
    import zipfile

    dataset_path = Path(dataset_path)

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset path does not exist: {dataset_path}"
        )

    # ------------------------------------------------------
    # Case 1: Azure ML URI_FOLDER
    # ------------------------------------------------------

    if dataset_path.is_dir():
        return dataset_path

    # ------------------------------------------------------
    # Case 2: ZIP file
    # ------------------------------------------------------

    if dataset_path.is_file():

        if dataset_path.suffix.lower() != ".zip":
            raise ValueError(
                f"Unsupported dataset file: {dataset_path}. "
                "Expected a .zip file."
            )

        extraction_root = (
            Path(tempfile.gettempdir())
            / "openvisionai_dataset"
        )

        # Remove previous extraction if it exists
        if extraction_root.exists():
            shutil.rmtree(
                extraction_root
            )

        extraction_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        # --------------------------------------------------
        # Extract ZIP
        # --------------------------------------------------

        with zipfile.ZipFile(
            dataset_path,
            "r",
        ) as archive:

            archive.extractall(
                extraction_root
            )

        # --------------------------------------------------
        # Find actual YOLO dataset root
        # --------------------------------------------------

        def is_yolo_root(path: Path) -> bool:

            yaml_candidates = (
                "dataset.yaml",
                "data.yaml",
                "dataset.yml",
                "data.yml",
            )

            has_yaml = any(
                (path / name).exists()
                for name in yaml_candidates
            )

            has_images = (
                path / "images"
            ).is_dir()

            has_labels = (
                path / "labels"
            ).is_dir()

            return (
                has_yaml
                and has_images
                and has_labels
            )

        # Direct root
        if is_yolo_root(
            extraction_root
        ):
            return extraction_root

        # Search nested directories
        for candidate in extraction_root.rglob("*"):

            if candidate.is_dir() and is_yolo_root(
                candidate
            ):
                return candidate

        raise ValueError(
            "ZIP was extracted successfully, but no valid "
            "YOLO dataset root was found. Expected a directory "
            "containing dataset.yaml/data.yaml, images/, and labels/."
        )

    # ------------------------------------------------------
    # Unsupported input
    # ------------------------------------------------------

    raise ValueError(
        f"Unsupported dataset input: {dataset_path}"
    )


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