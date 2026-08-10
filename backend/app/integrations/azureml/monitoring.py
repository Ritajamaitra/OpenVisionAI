"""
OpenVisionAI Azure ML Monitoring Client

Responsibilities
----------------
1. Retrieve Azure ML job status
2. Wait for job completion
3. Download Azure ML output artifacts
4. Read metrics.json
5. Read summary.json
6. Download logs
"""

import json
import shutil
import tempfile
from pathlib import Path
from time import sleep

from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
)

from app.integrations.azureml.client import (
    get_azure_ml_client,
)

from app.integrations.azureml.contracts import (
    AzureJobMetrics,
)

from app.integrations.azureml.exceptions import (
    JobMetricsException,
    JobNotFoundException,
)


class AzureMonitoringClient:
    """Monitor OpenVisionAI training jobs running on Azure ML."""

    TERMINAL_STATUSES = {
        "COMPLETED",
        "FAILED",
        "CANCELED",
    }

    def __init__(self):
        self.client = get_azure_ml_client().client

    # ==========================================================
    # Job Status
    # ==========================================================

    def get_status(
        self,
        job_name: str,
    ) -> str:
        try:
            job = self.client.jobs.get(job_name)
            return str(job.status)

        except ResourceNotFoundError as exc:
            raise JobNotFoundException(
                f"Job '{job_name}' not found."
            ) from exc

    # ==========================================================
    # Wait for Completion
    # ==========================================================

    def wait_for_completion(
        self,
        job_name: str,
        poll_interval: int = 10,
    ) -> str:
        while True:
            status = self.get_status(job_name)

            if status.upper() in self.TERMINAL_STATUSES:
                return status

            sleep(poll_interval)

    # ==========================================================
    # Download / Read JSON Artifact
    # ==========================================================

    def _read_json_artifact(
        self,
        job_name: str,
        artifact_name: str,
    ) -> dict:
        temp_dir = Path(
            tempfile.mkdtemp(
                prefix="openvisionai_"
            )
        )

        try:
            self.client.jobs.download(
                name=job_name,
                download_path=str(temp_dir),
                output_name="outputs",
            )

            artifact = (
                temp_dir
                / "outputs"
                / artifact_name
            )

            if not artifact.exists():
                raise FileNotFoundError(
                    f"Azure ML output artifact not found: "
                    f"outputs/{artifact_name}"
                )

            with open(
                artifact,
                "r",
                encoding="utf-8",
            ) as file:
                return json.load(file)

        except (
            HttpResponseError,
            json.JSONDecodeError,
            OSError,
        ) as exc:
            raise JobMetricsException(
                f"Failed to read Azure ML artifact "
                f"'{artifact_name}' for job "
                f"'{job_name}': {exc}"
            ) from exc

        finally:
            shutil.rmtree(
                temp_dir,
                ignore_errors=True,
            )

    # ==========================================================
    # Download Logs
    # ==========================================================

    def download_logs(
        self,
        job_name: str,
        destination: str | Path,
    ) -> Path:
        destination = Path(destination)

        destination.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:
            self.client.jobs.download(
                name=job_name,
                download_path=str(destination),
                output_name="logs",
            )

        except (
            HttpResponseError,
            ResourceNotFoundError,
        ) as exc:
            raise JobMetricsException(
                f"Failed to download logs for "
                f"job '{job_name}': {exc}"
            ) from exc

        return destination

    # ==========================================================
    # Metrics
    # ==========================================================

    def get_metrics(
        self,
        job_name: str,
    ) -> AzureJobMetrics:
        metrics = self._read_json_artifact(
            job_name,
            "metrics.json",
        )

        try:
            return AzureJobMetrics(
                precision=float(
                    metrics.get("precision", 0)
                ),
                recall=float(
                    metrics.get("recall", 0)
                ),
                map50=float(
                    metrics.get("map50", 0)
                ),
                map50_95=float(
                    metrics.get("map50_95", 0)
                ),
                training_time=float(
                    metrics.get("training_time", 0)
                ),
            )

        except (
            TypeError,
            ValueError,
        ) as exc:
            raise JobMetricsException(
                f"Invalid metrics.json for "
                f"job '{job_name}': {exc}"
            ) from exc

    # ==========================================================
    # Training Summary
    # ==========================================================

    def get_summary(
        self,
        job_name: str,
    ) -> dict:
        return self._read_json_artifact(
            job_name,
            "summary.json",
        )