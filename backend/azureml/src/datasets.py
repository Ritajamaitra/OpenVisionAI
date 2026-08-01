"""
Dataset utilities for OpenVisionAI.

Responsibilities:
- Extract ZIP datasets
- Locate dataset YAML
- Validate dataset structure
- Return dataset root
"""

from pathlib import Path
from zipfile import ZipFile
import logging
import tempfile

from utils import read_yaml


SUPPORTED_YAML_FILES = (
    "dataset.yaml",
    "data.yaml",
    "dataset.yml",
    "data.yml",
)


def extract_dataset(zip_path: str | Path) -> Path:
    """
    Extract a ZIP dataset into a temporary directory.

    Parameters
    ----------
    zip_path : str | Path

    Returns
    -------
    Path
        Extraction directory.
    """

    zip_path = Path(zip_path)

    if not zip_path.exists():
        raise FileNotFoundError(f"Dataset not found: {zip_path}")

    extract_dir = Path(tempfile.mkdtemp(prefix="openvisionai_dataset_"))

    with ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    return extract_dir


def find_data_yaml(dataset_root: str | Path) -> Path:
    """
    Locate dataset.yaml or data.yaml recursively.

    Parameters
    ----------
    dataset_root : str | Path

    Returns
    -------
    Path
    """

    dataset_root = Path(dataset_root)

    for yaml_name in SUPPORTED_YAML_FILES:
        matches = list(dataset_root.rglob(yaml_name))

        if matches:
            return matches[0]

    raise FileNotFoundError(
        "No dataset YAML found. "
        f"Expected one of {SUPPORTED_YAML_FILES}"
    )


def validate_dataset(dataset_root: str | Path) -> tuple[Path, dict]:
    """
    Validate dataset using the YAML.

    Supports any valid Ultralytics dataset layout.

    Returns
    -------
    tuple
        (
            dataset_directory,
            yaml_config
        )
    """

    dataset_root = Path(dataset_root)

    yaml_path = find_data_yaml(dataset_root)

    config = read_yaml(yaml_path)

    dataset_dir = yaml_path.parent

    required_keys = ["train", "val", "names"]

    missing = [k for k in required_keys if k not in config]

    if missing:
        raise ValueError(
            f"dataset.yaml missing required keys: {missing}"
        )

    splits = {
        "train": config["train"],
        "val": config["val"],
    }

    for split_name, split_path in splits.items():

        resolved = (dataset_dir / split_path).resolve()

        if not resolved.exists():
            raise ValueError(
                f"{split_name} path does not exist:\n{resolved}"
            )

    return dataset_dir, config


def print_dataset_info(
    dataset_dir: Path,
    config: dict,
    logger: logging.Logger,
):
    """
    Print dataset information.
    """

    logger.info("=" * 60)
    logger.info("Dataset Information")
    logger.info("=" * 60)

    logger.info("Dataset Root : %s", dataset_dir)

    logger.info("Train Path   : %s", config["train"])
    logger.info("Val Path     : %s", config["val"])

    logger.info("Classes      : %s", len(config["names"]))

    logger.info("Class Names")

    if isinstance(config["names"], dict):
        for idx, name in config["names"].items():
            logger.info("%s -> %s", idx, name)

    else:
        for idx, name in enumerate(config["names"]):
            logger.info("%s -> %s", idx, name)

    logger.info("=" * 60)