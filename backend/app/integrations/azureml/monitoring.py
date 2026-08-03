"""
OpenVisionAI Azure ML Monitoring Client

Responsible for monitoring Azure ML jobs.

This module provides:

- Job Status
- Metrics
- Outputs
- Logs
- Waiting for completion/
"""

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

    def __init__(self):

        self.client = get_azure_ml_client().client

    # ==========================================================
    # Status
    # ==========================================================

    def get_status(
        self,
        job_name: str,
    ) -> str:

        try:

            job = self.client.jobs.get(job_name)

            return job.status

        except ResourceNotFoundError as ex:

            raise JobNotFoundException(
                f"Job '{job_name}' not found."
            ) from ex

    # ==========================================================
    # Wait Until Finished
    # ==========================================================

    def wait_for_completion(
        self,
        job_name: str,
        poll_interval: int = 10,
    ) -> str:

        while True:

            status = self.get_status(job_name)

            if status in (
                "Completed",
                "Failed",
                "Canceled",
            ):
                return status

            sleep(poll_interval)

    # ==========================================================
    # Metrics
    # ==========================================================

    def get_metrics(
        self,
        job_name: str,
    ) -> AzureJobMetrics:

        try:

            job = self.client.jobs.get(job_name)

            outputs = getattr(
                job,
                "properties",
                None,
            )

            metrics = {}

            if outputs is not None:

                metrics = getattr(
                    outputs,
                    "properties",
                    {},
                )

            return AzureJobMetrics(

                precision=float(
                    metrics.get(
                        "precision",
                        0,
                    )
                ),

                recall=float(
                    metrics.get(
                        "recall",
                        0,
                    )
                ),

                map50=float(
                    metrics.get(
                        "map50",
                        0,
                    )
                ),

                map50_95=float(
                    metrics.get(
                        "map50_95",
                        0,
                    )
                ),

                training_time=float(
                    metrics.get(
                        "training_time",
                        0,
                    )
                ),
            )

        except HttpResponseError as ex:

            raise JobMetricsException(
                str(ex)
            ) from ex

    # ==========================================================
    # Outputs
    # ==========================================================

    def get_outputs(
        self,
        job_name: str,
        output_path: str,
    ) -> Path:

        destination = Path(output_path)

        destination.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.client.jobs.download(
            name=job_name,
            download_path=str(destination),
            output_name="outputs",
        )

        return destination

    # ==========================================================
    # Logs
    # ==========================================================

    def get_logs(
        self,
        job_name: str,
        output_path: str,
    ) -> Path:

        destination = Path(output_path)

        destination.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.client.jobs.download(
            name=job_name,
            download_path=str(destination),
            output_name="logs",
        )

        return destination