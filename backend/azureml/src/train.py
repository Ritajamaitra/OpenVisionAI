"""
Entry point for OpenVisionAI Azure ML training.
"""

import argparse
import json
import sys
from pathlib import Path
import mlflow

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
        help="Path to dataset ZIP"
    )

    parser.add_argument(
        "--model",
        type=str,
        default="yolov8n.pt"
    )

    parser.add_argument(
        "--epochs",
        type=int,
        default=50
    )

    parser.add_argument(
        "--imgsz",
        type=int,
        default=640
    )

    parser.add_argument(
        "--batch",
        type=int,
        default=16
    )

    parser.add_argument(
        "--project",
        type=str,
        default="outputs"
    )

    parser.add_argument(
        "--name",
        type=str,
        default="train"
    )

    parser.add_argument(
        "--device",
        type=str,
        default="cpu"
    )

    return parser.parse_args()


def main():

    logger = setup_logging()

    try:

        args = parse_args()

        logger.info("=" * 70)
        logger.info("OpenVisionAI Training Started")
        logger.info("=" * 70)

        logger.info("Dataset ZIP : %s", args.dataset)
        logger.info("Model       : %s", args.model)
        logger.info("Epochs      : %d", args.epochs)
        logger.info("Image Size  : %d", args.imgsz)
        logger.info("Batch Size  : %d", args.batch)
        logger.info("Device      : %s", args.device)

        logger.info("Extracting dataset...")

        extracted_dir = extract_dataset(args.dataset)

        logger.info("Dataset extracted to:")
        logger.info(extracted_dir)

        print_directory_tree(extracted_dir, logger)

        dataset_dir, config = validate_dataset(extracted_dir)

        print_dataset_info(
            dataset_dir,
            config,
            logger,
        )

        yaml_file = None

        for candidate in (
            "dataset.yaml",
            "data.yaml",
            "dataset.yml",
            "data.yml",
        ):
            path = dataset_dir / candidate
            if path.exists():
                yaml_file = path
                break

        if yaml_file is None:
            raise FileNotFoundError(
                "Dataset YAML not found after validation."
            )

        logger.info("Dataset YAML:")
        logger.info(yaml_file)

        logger.info("=" * 70)
        logger.info("Starting YOLO Training")
        logger.info("=" * 70)

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
        metrics = training_result["metrics"]

        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                mlflow.log_metric(key, float(value))

        mlflow.log_param("model", args.model)
        mlflow.log_param("epochs", args.epochs)
        mlflow.log_param("batch_size", args.batch)
        mlflow.log_param("imgsz", args.imgsz)

        mlflow.log_artifact(training_result["best_model"])
        logger.info("=" * 70)
        logger.info("Training Completed")
        logger.info("=" * 70)

        logger.info(
            json.dumps(
                training_result,
                indent=4,
                default=str,
            )
        )

        logger.info("Best Model : %s", training_result["best_model"])
        logger.info("Last Model : %s", training_result["last_model"])
        logger.info("Save Dir   : %s", training_result["save_dir"])

        logger.info("Metrics")

        for key, value in training_result["metrics"].items():
            logger.info("%s : %s", key, value)

        logger.info("=" * 70)
        logger.info("OpenVisionAI Training Finished Successfully")
        logger.info("=" * 70)

    except Exception as e:

        logger.exception("Training failed.")

        sys.exit(1)


if __name__ == "__main__":
    main()