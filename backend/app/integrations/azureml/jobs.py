"""
OpenVisionAI Azure Jobs Client

Responsibilities
----------------
1. Submit Azure ML training jobs
2. Retrieve Azure ML jobs
3. List Azure ML jobs
4. Cancel running jobs
5. Download job outputs

This module isolates the Azure ML SDK from the
rest of OpenVisionAI.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from azure.ai.ml import Input, command
from azure.ai.ml.constants import AssetTypes
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
)

from app.config.settings import settings

from app.integrations.azureml.client import (
    get_azure_ml_client,
)

from app.integrations.azureml.contracts import (
    AzureJob,
    TrainingJobRequest,
)

from app.integrations.azureml.exceptions import (
    JobCancellationException,
    JobNotFoundException,
    JobSubmissionException,
)


class AzureJobsClient:

    def __init__(self):

        self.client = get_azure_ml_client().client

    # ==========================================================
    # Helpers
    # ==========================================================

    @staticmethod
    def _created_at(job) -> Optional[datetime]:
        """
        Azure SDK exposes creation timestamps differently
        across SDK versions.

        This helper normalizes the value.
        """

        creation = getattr(
            job,
            "creation_context",
            None,
        )

        if creation is not None:

            for attribute in (

                "created_at",

                "created_time",

                "creation_time",

                "createdOn",

            ):

                value = getattr(
                    creation,
                    attribute,
                    None,
                )

                if value is not None:

                    return value

        system_data = getattr(
            job,
            "system_data",
            None,
        )

        if system_data is not None:

            for attribute in (

                "created_at",

                "createdAt",

            ):

                value = getattr(
                    system_data,
                    attribute,
                    None,
                )

                if value is not None:

                    return value

        return None

    @classmethod
    def _to_contract(
        cls,
        job,
    ) -> AzureJob:
        """
        Convert Azure SDK Job
        into OpenVisionAI contract.
        """

        return AzureJob(

            name=job.name,

            display_name=getattr(
                job,
                "display_name",
                job.name,
            ),

            status=getattr(
                job,
                "status",
                "Unknown",
            ),

            experiment_name=getattr(
                job,
                "experiment_name",
                "",
            ),

            created_at=cls._created_at(
                job,
            ),

        )

    # ==========================================================
    # Submit Training Job
    # ==========================================================

    def submit_training_job(
        self,
        request: TrainingJobRequest,
    ) -> AzureJob:

        try:

            aml_job = command(

                code=settings.azure_training_code_path,

                command=(

                    "python src/train.py "

                    "--dataset ${{inputs.dataset}} "

                    f"--model {request.model_name} "

                    f"--epochs {request.epochs} "

                    f"--imgsz {request.imgsz} "

                    f"--batch {request.batch}"

                ),

                inputs={

                    "dataset": Input(

                        type=AssetTypes.URI_FILE,

                        path=request.dataset_uri,

                    )

                },

                environment=(

                    f"{request.environment_name}:"

                    f"{request.environment_version}"

                ),

                compute=request.compute_name,

                experiment_name=request.experiment_name,

                display_name=request.display_name,

            )

            created_job = self.client.jobs.create_or_update(
                aml_job
            )

            return self._to_contract(
                created_job
            )

        except HttpResponseError as ex:

            raise JobSubmissionException(
                str(ex)
            ) from ex

    # ==========================================================
    # Get Job
    # ==========================================================

    def get_job(
        self,
        job_name: str,
    ) -> AzureJob:

        try:

            job = self.client.jobs.get(
                job_name
            )

            return self._to_contract(
                job
            )

        except ResourceNotFoundError as ex:

            raise JobNotFoundException(

                f"Job '{job_name}' not found."

            ) from ex

        # ==========================================================
    # List Jobs
    # ==========================================================

    def list_jobs(
        self,
    ) -> list[AzureJob]:
        """
        Return all Azure ML jobs.
        """

        return [

            self._to_contract(job)

            for job in self.client.jobs.list()

        ]

    # ==========================================================
    # Cancel Job
    # ==========================================================

    def cancel_job(
        self,
        job_name: str,
    ) -> None:
        """
        Cancel a running Azure ML job.
        """

        try:

            self.client.jobs.begin_cancel(
                job_name
            ).wait()

        except ResourceNotFoundError as ex:

            raise JobNotFoundException(

                f"Job '{job_name}' not found."

            ) from ex

        except HttpResponseError as ex:

            raise JobCancellationException(

                str(ex)

            ) from ex

    # ==========================================================
    # Download Outputs
    # ==========================================================

    def download_outputs(
        self,
        job_name: str,
        download_path: str | Path,
    ) -> Path:
        """
        Download all outputs produced by an Azure ML job.

        Returns
        -------
        Path
            Local download directory.
        """

        destination = Path(download_path)

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

            return destination

        except ResourceNotFoundError as ex:

            raise JobNotFoundException(

                f"Job '{job_name}' not found."

            ) from ex

        except HttpResponseError as ex:

            raise JobSubmissionException(

                str(ex)

            ) from ex

    # ==========================================================
    # Stream Logs
    # ==========================================================

    def stream_logs(
        self,
        job_name: str,
    ) -> None:
        """
        Stream live Azure ML logs to the console.
        Useful during development.
        """

        try:

            self.client.jobs.stream(
                job_name
            )

        except ResourceNotFoundError as ex:

            raise JobNotFoundException(

                f"Job '{job_name}' not found."

            ) from ex

        except HttpResponseError as ex:

            raise JobSubmissionException(

                str(ex)

            ) from ex