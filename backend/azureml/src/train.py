"""
OpenVisionAI Azure ML Training Entry Point

Responsibilities
----------------
1. Parse command-line arguments
2. Extract and validate dataset
3. Launch YOLO training
4. Log parameters, metrics and artifacts to MLflow
5. Return a clean training summary
"""

import argparse
import json
import sys
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


# ---------------------------------------------------------
# Argument Parser
# ---------------------------------------------------------

def parse_args():

    parser = argparse.ArgumentParser(
        description="OpenVisionAI YOLO Trainer"
    )

    parser.add_argument(
        "--dataset",
        type=str,
        required=True,
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


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    logger = setup_logging()

    try:

        args = parse_args()

        logger.info("=" * 70)
        logger.info("OpenVisionAI Training Started")
        logger.info("=" * 70)

        logger.info("Dataset : %s", args.dataset)
        logger.info("Model   : %s", args.model)

        # -------------------------------------------------
        # Extract Dataset
        # -------------------------------------------------

        extracted_dir = extract_dataset(args.dataset)

        logger.info("Dataset extracted to:")
        logger.info(extracted_dir)

        print_directory_tree(
            extracted_dir,
            logger,
        )

        dataset_dir, config = validate_dataset(
            extracted_dir
        )

        print_dataset_info(
            dataset_dir,
            config,
            logger,
        )

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
                "Dataset YAML not found."
            )

        logger.info("Dataset YAML:")
        logger.info(yaml_file)

        # -------------------------------------------------
        # Train
        # -------------------------------------------------

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

        
        # -------------------------------------------------
        # Logs
        # -------------------------------------------------

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

        logger.info("=" * 70)
        logger.info("Metrics")
        logger.info("=" * 70)

        for key, value in training_result["metrics"].items():

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