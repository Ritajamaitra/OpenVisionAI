"""
OpenVisionAI Azure Jobs Client

Handles Azure Machine Learning command jobs.
"""

from pathlib import Path
from typing import List

from azure.ai.ml import Input, command
from azure.ai.ml.constants import AssetTypes
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
from app.config.settings import settings
from app.integrations.azureml.client import get_azure_ml_client
from app.integrations.azureml.contracts import (
    AzureJob,
    TrainingJobRequest,
)
from app.integrations.azureml.exceptions import (
    JobSubmissionException,
    JobNotFoundException,
    JobCancellationException,
)


class AzureJobsClient:

    def __init__(self):

        self.client = get_azure_ml_client().client

    # ==========================================================
    # Submit Training Job
    # ==========================================================

    def submit_training_job(
        self,
        request: TrainingJobRequest,
    ) -> AzureJob:

        try:

            job = command(

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

            created_job = self.client.jobs.create_or_update(job)

            return AzureJob(
                name=created_job.name,
                display_name=created_job.display_name,
                status=created_job.status,
                experiment_name=created_job.experiment_name,
                created_at=created_job.creation_context.created_time,
            )

        except HttpResponseError as ex:

            raise JobSubmissionException(str(ex)) from ex

    # ==========================================================
    # Get Job
    # ==========================================================

    def get_job(
        self,
        job_name: str,
    ) -> AzureJob:

        try:

            job = self.client.jobs.get(job_name)

            return AzureJob(
                name=job.name,
                display_name=job.display_name,
                status=job.status,
                experiment_name=job.experiment_name,
                created_at=job.creation_context.created_time,
            )

        except ResourceNotFoundError as ex:

            raise JobNotFoundException(
                f"Job '{job_name}' not found."
            ) from ex

    # ==========================================================
    # List Jobs
    # ==========================================================

    def list_jobs(self) -> List[AzureJob]:

        jobs = []

        for job in self.client.jobs.list():

            jobs.append(

                AzureJob(
                    name=job.name,
                    display_name=job.display_name,
                    status=job.status,
                    experiment_name=job.experiment_name,
                    created_at=job.creation_context.created_time,
                )

            )

        return jobs

    # ==========================================================
    # Cancel Job
    # ==========================================================

    def cancel_job(
        self,
        job_name: str,
    ) -> None:

        try:

            self.client.jobs.begin_cancel(job_name).wait()

        except HttpResponseError as ex:

            raise JobCancellationException(str(ex)) from ex

    # ==========================================================
    # Download Outputs
    # ==========================================================

    def download_outputs(
        self,
        job_name: str,
        download_path: str,
    ) -> Path:

        destination = Path(download_path)

        destination.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.client.jobs.download(
            name=job_name,
            download_path=str(destination),
            all=True,
        )

        return destination