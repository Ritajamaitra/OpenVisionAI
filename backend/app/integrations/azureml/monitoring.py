"""
OpenVisionAI Azure ML Monitoring Client
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
    """Monitor Azure ML training jobs."""

    TERMINAL_STATUSES = {
        "COMPLETED",
        "FAILED",
        "CANCELED",
        "CANCELLED",
    }

    def __init__(self):
        self.client = get_azure_ml_client().client

    # ==========================================================
    # JOB STATUS
    # ==========================================================

    def get_status(self, job_name: str) -> str:

        try:
            job = self.client.jobs.get(job_name)

            return str(job.status).upper()

        except ResourceNotFoundError as exc:

            raise JobNotFoundException(
                f"Azure ML job '{job_name}' was not found."
            ) from exc

    # ==========================================================
    # WAIT FOR COMPLETION
    # ==========================================================

    def wait_for_completion(
        self,
        job_name: str,
        poll_interval: int = 10,
    ) -> str:

        while True:

            status = self.get_status(job_name)

            if status in self.TERMINAL_STATUSES:
                return status

            sleep(poll_interval)

    # ==========================================================
    # DOWNLOAD ALL JOB ARTIFACTS
    # ==========================================================

    def _download_job(
        self,
        job_name: str,
    ) -> Path:

        temp_dir = Path(
            tempfile.mkdtemp(
                prefix="openvisionai_"
            )
        )

        try:

            # IMPORTANT:
            # Do NOT use output_name="outputs".
            #
            # "outputs" is the default artifact directory,
            # not necessarily a named Azure ML output.

            self.client.jobs.download(
                name=job_name,
                download_path=str(temp_dir),
                all=True,
            )

            return temp_dir

        except Exception:

            shutil.rmtree(
                temp_dir,
                ignore_errors=True,
            )

            raise

    # ==========================================================
    # FIND ARTIFACT
    # ==========================================================

    @staticmethod
    def _find_artifact(
        root: Path,
        filename: str,
    ) -> Path:

        matches = list(
            root.rglob(filename)
        )

        if not matches:

            raise FileNotFoundError(
                f"Could not find '{filename}' "
                f"inside downloaded Azure ML job artifacts."
            )

        # Prefer the artifact under outputs/
        for match in matches:

            if "outputs" in match.parts:
                return match

        return matches[0]

    # ==========================================================
    # READ JSON ARTIFACT
    # ==========================================================

    def _read_json_artifact(
        self,
        job_name: str,
        artifact_name: str,
    ) -> dict:

        temp_dir = None

        try:

            temp_dir = self._download_job(
                job_name
            )

            artifact = self._find_artifact(
                temp_dir,
                artifact_name,
            )

            with open(
                artifact,
                "r",
                encoding="utf-8",
            ) as file:

                return json.load(file)

        except FileNotFoundError as exc:

            raise JobMetricsException(
                f"Azure ML artifact "
                f"'{artifact_name}' was not found "
                f"for job '{job_name}'."
            ) from exc

        except json.JSONDecodeError as exc:

            raise JobMetricsException(
                f"Artifact '{artifact_name}' "
                f"contains invalid JSON for "
                f"job '{job_name}'."
            ) from exc

        except (
            HttpResponseError,
            OSError,
        ) as exc:

            raise JobMetricsException(
                f"Failed to download/read "
                f"'{artifact_name}' for "
                f"job '{job_name}': {exc}"
            ) from exc

        finally:

            if temp_dir:

                shutil.rmtree(
                    temp_dir,
                    ignore_errors=True,
                )

    # ==========================================================
    # METRICS
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
                    metrics["precision"]
                ),
                recall=float(
                    metrics["recall"]
                ),
                map50=float(
                    metrics["map50"]
                ),
                map50_95=float(
                    metrics["map50_95"]
                ),
                training_time=float(
                    metrics["training_time"]
                ),
            )

        except (
            KeyError,
            TypeError,
            ValueError,
        ) as exc:

            raise JobMetricsException(
                f"Invalid metrics.json for "
                f"job '{job_name}': {exc}. "
                f"Received: {metrics}"
            ) from exc

    # ==========================================================
    # SUMMARY
    # ==========================================================

    def get_summary(
        self,
        job_name: str,
    ) -> dict:

        return self._read_json_artifact(
            job_name,
            "summary.json",
        )

    # ==========================================================
    # LOGS
    # ==========================================================

    def download_logs(
        self,
        job_name: str,
        destination: str | Path,
    ) -> Path:

        destination = Path(
            destination
        )

        destination.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:

            self.client.jobs.download(
                name=job_name,
                download_path=str(destination),
                all=True,
            )

        except (
            HttpResponseError,
            ResourceNotFoundError,
        ) as exc:

            raise JobMetricsException(
                f"Failed to download logs "
                f"for job '{job_name}': {exc}"
            ) from exc

        return destination