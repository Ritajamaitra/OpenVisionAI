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
            time.time() - start_time,2,)
    
        # -------------------------------------------------
        # Logs
        # -------------------------------------------------

        logger.info("=" * 70)
        logger.info("Training Completed")
        logger.info("=" * 70)

        # -------------------------------------------------
        # Azure ML Output Contract
        # -------------------------------------------------

        outputs_dir = Path("outputs")
        outputs_dir.mkdir(
            parents=True,
            exist_ok=True,
            )
        models_dir = outputs_dir / "models"
        models_dir.mkdir(exist_ok=True,)

        best_model = Path(training_result["best_model"])
        last_model = Path(training_result["last_model"])

        if best_model.exists():
            shutil.copy2(best_model,models_dir / "best.pt",)

        if last_model.exists():
            shutil.copy2(last_model,models_dir / "last.pt",)

        metrics = training_result["metrics"]
        metrics_json = {
            "precision": float(
                metrics.get(
                    "metrics/precision(B)",
                    metrics.get(
                        "precision",0,
            ),
        )
    ),

            "recall": float(
                metrics.get(
                    "metrics/recall(B)",
                    metrics.get(
                "recall",0,
            ),
        )
    ),

            "map50": float(
                metrics.get(
                    "metrics/mAP50(B)",
                    metrics.get(
                "map50",0,
            ),
        )
    ),

            "map50_95": float(
                metrics.get(
                    "metrics/mAP50-95(B)",
                    metrics.get(
                "map50_95",
                0,
            ),
        )
    ),

            "training_time": training_time,
}

        logger.info(
            json.dumps(
                training_result,
                indent=4,
                default=str,
            )
        )

        with open(
           outputs_dir / "metrics.json","w",) as f:
           json.dump(
             metrics_json,
             f,
             indent=4,)

        summary = {

    "status": "COMPLETED",

    "model": args.model,

    "epochs": args.epochs,

    "imgsz": args.imgsz,

    "batch": args.batch,

    "dataset": str(yaml_file),

    "best_model": str(
        models_dir / "best.pt"
    ),

    "last_model": str(
        models_dir / "last.pt"
    ),
}


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