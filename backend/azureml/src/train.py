"""
OpenVisionAI Azure ML Training Entry Point

Responsibilities
----------------
1. Parse command-line arguments
2. Resolve an Azure ML URI-folder or local ZIP dataset
3. Validate the YOLO dataset
4. Launch YOLO training
5. Write Azure ML output artifacts
"""

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

from datasets import (
    extract_dataset,
    validate_dataset,
    print_dataset_info,
)

from trainer import train_model

from utils import (
    setup_logging,
    print_directory_tree,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="OpenVisionAI YOLO Trainer"
    )

    parser.add_argument(
        "--dataset",
        type=str,
        required=True,
        help="Azure ML mounted dataset directory or ZIP file.",
    )

    parser.add_argument(
        "--model",
        default="yolov8n.pt",
    )

    parser.add_argument(
        "--epochs",
        type=int,
        default=50,
    )

    parser.add_argument(
        "--imgsz",
        type=int,
        default=640,
    )

    parser.add_argument(
        "--batch",
        type=int,
        default=16,
    )

    parser.add_argument(
        "--project",
        default="outputs",
    )

    parser.add_argument(
        "--name",
        default="train",
    )

    parser.add_argument(
        "--device",
        default="cpu",
    )

    return parser.parse_args()


def _safe_float(value, default=0.0):
    """Convert a metric to float without allowing one bad value to fail the job."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _resolve_dataset(dataset_input: str, logger) -> Path:
    """
    Azure ML uri_folder inputs are mounted as directories.

    Older/local workflows may pass a ZIP file. Support both so the
    same training entry point works in Azure ML and locally.
    """
    dataset_path = Path(dataset_input)

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset input does not exist: {dataset_path}"
        )

    if dataset_path.is_dir():
        logger.info("Dataset input is already a directory.")
        return dataset_path

    if dataset_path.is_file():
        logger.info("Dataset input is a file; extracting dataset.")
        extracted_dir = extract_dataset(str(dataset_path))
        return Path(extracted_dir)

    raise ValueError(
        f"Unsupported dataset input: {dataset_path}"
    )


def main():
    logger = setup_logging()

    try:
        args = parse_args()

        logger.info("=" * 70)
        logger.info("OpenVisionAI Training Started")
        logger.info("=" * 70)
        logger.info("Dataset : %s", args.dataset)
        logger.info("Model   : %s", args.model)
        logger.info("Epochs  : %s", args.epochs)
        logger.info("ImageSz : %s", args.imgsz)
        logger.info("Batch   : %s", args.batch)
        logger.info("Device  : %s", args.device)

        # -----------------------------------------------------
        # Resolve dataset
        # -----------------------------------------------------

        dataset_root = _resolve_dataset(
            args.dataset,
            logger,
        )

        logger.info("Dataset root:")
        logger.info("%s", dataset_root)

        print_directory_tree(
            dataset_root,
            logger,
        )

        dataset_dir, config = validate_dataset(
            dataset_root
        )

        print_dataset_info(
            dataset_dir,
            config,
            logger,
        )

        # -----------------------------------------------------
        # Locate dataset YAML
        # -----------------------------------------------------

        yaml_file = None

        for filename in (
            "dataset.yaml",
            "dataset.yml",
            "data.yaml",
            "data.yml",
        ):
            candidate = dataset_dir / filename

            if candidate.exists():
                yaml_file = candidate
                break

        if yaml_file is None:
            raise FileNotFoundError(
                f"Dataset YAML not found under {dataset_dir}"
            )

        logger.info("Dataset YAML: %s", yaml_file)

        # -----------------------------------------------------
        # Train
        # -----------------------------------------------------

        start_time = time.time()

        training_result = train_model(
            dataset_yaml=yaml_file,
            model_name=args.model,
            epochs=args.epochs,
            imgsz=args.imgsz,
            batch=args.batch,
            project=args.project,
            experiment=args.name,
            device=args.device,
        )

        training_time = round(
            time.time() - start_time,
            2,
        )

        # -----------------------------------------------------
        # Azure ML output contract
        # -----------------------------------------------------

        outputs_dir = Path("outputs")
        outputs_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        models_dir = outputs_dir / "models"
        models_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        best_model = Path(
            training_result["best_model"]
        )

        last_model = Path(
            training_result["last_model"]
        )

        if best_model.exists():
            shutil.copy2(
                best_model,
                models_dir / "best.pt",
            )
        else:
            logger.warning(
                "Best model was not found: %s",
                best_model,
            )

        if last_model.exists():
            shutil.copy2(
                last_model,
                models_dir / "last.pt",
            )
        else:
            logger.warning(
                "Last model was not found: %s",
                last_model,
            )

        # -----------------------------------------------------
        # Metrics
        # -----------------------------------------------------

        metrics = training_result.get(
            "metrics",
            {},
        )

        metrics_json = {
            "precision": _safe_float(
                metrics.get(
                    "metrics/precision(B)",
                    metrics.get("precision", 0),
                )
            ),
            "recall": _safe_float(
                metrics.get(
                    "metrics/recall(B)",
                    metrics.get("recall", 0),
                )
            ),
            "map50": _safe_float(
                metrics.get(
                    "metrics/mAP50(B)",
                    metrics.get("map50", 0),
                )
            ),
            "map50_95": _safe_float(
                metrics.get(
                    "metrics/mAP50-95(B)",
                    metrics.get("map50_95", 0),
                )
            ),
            "training_time": training_time,
        }

        metrics_path = outputs_dir / "metrics.json"

        with open(
            metrics_path,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                metrics_json,
                file,
                indent=4,
            )

        # -----------------------------------------------------
        # Summary
        # -----------------------------------------------------

        summary = {
            "status": "COMPLETED",
            "model": args.model,
            "epochs": args.epochs,
            "imgsz": args.imgsz,
            "batch": args.batch,
            "device": args.device,
            "dataset": str(yaml_file),
            "best_model": str(
                models_dir / "best.pt"
            ),
            "last_model": str(
                models_dir / "last.pt"
            ),
            "metrics": metrics_json,
        }

        summary_path = outputs_dir / "summary.json"

        with open(
            summary_path,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                summary,
                file,
                indent=4,
            )

        # -----------------------------------------------------
        # Logging
        # -----------------------------------------------------

        logger.info("Best Model : %s", best_model)
        logger.info("Last Model : %s", last_model)
        logger.info("Metrics    : %s", metrics_path)
        logger.info("Summary    : %s", summary_path)

        logger.info("=" * 70)
        logger.info("Metrics")
        logger.info("=" * 70)

        for key, value in metrics_json.items():
            logger.info(
                "%s : %s",
                key,
                value,
            )

        logger.info("=" * 70)
        logger.info("OpenVisionAI Training Finished Successfully")
        logger.info("=" * 70)

    except Exception:
        logger.exception(
            "Training failed."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()