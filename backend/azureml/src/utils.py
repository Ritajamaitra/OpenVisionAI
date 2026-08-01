"""
Utility functions for OpenVisionAI Azure ML training.

Contains:
- Logging configuration
- YAML reader
- Directory tree printer
"""

import logging
from pathlib import Path
from typing import Dict, Any

import yaml


def setup_logging() -> logging.Logger:
    """
    Configure application logger.

    Returns
    -------
    logging.Logger
        Configured logger instance.
    """

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    logger = logging.getLogger("OpenVisionAI")

    return logger


def read_yaml(yaml_path: str | Path) -> Dict[str, Any]:
    """
    Read YAML configuration.

    Parameters
    ----------
    yaml_path : str | Path

    Returns
    -------
    dict
    """

    yaml_path = Path(yaml_path)

    if not yaml_path.exists():
        raise FileNotFoundError(f"YAML not found: {yaml_path}")

    with open(yaml_path, "r") as f:
        return yaml.safe_load(f)


def print_directory_tree(root: str | Path, logger: logging.Logger) -> None:
    """
    Print dataset directory tree.

    Parameters
    ----------
    root : str | Path
    logger : logging.Logger
    """

    root = Path(root)

    logger.info("=" * 60)
    logger.info("Dataset Directory Structure")
    logger.info("=" * 60)

    for path in sorted(root.rglob("*")):
        try:
            relative = path.relative_to(root)
            logger.info(relative)
        except Exception:
            logger.info(path)

    logger.info("=" * 60)


def print_dataset_summary(dataset_yaml: dict, logger: logging.Logger):
    """
    Print parsed dataset.yaml.
    """

    logger.info("Dataset Configuration")

    for key, value in dataset_yaml.items():
        logger.info("%s : %s", key, value)