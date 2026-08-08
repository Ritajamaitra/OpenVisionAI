"""
OpenVisionAI Azure Model Registry Client

Responsibilities
----------------
1. Register trained models
2. Retrieve registered models
3. List registered models
4. Delete registered models

This module only communicates with the Azure ML
Model Registry.
"""

import shutil
import tempfile
from pathlib import Path

from azure.ai.ml.entities import Model
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
)

from app.integrations.azureml.client import (
    get_azure_ml_client,
)

from app.integrations.azureml.contracts import (
    AzureModel,
)

from app.integrations.azureml.exceptions import (
    ModelRegistrationException,
    ModelNotFoundException,
)


class AzureRegistryClient:

    def __init__(self):

        self.client = get_azure_ml_client().client

    # ==========================================================
    # Download Best Model
    # ==========================================================

    def _download_best_model(
        self,
        job_name: str,
    ) -> Path:
        """
        Downloads outputs/models/best.pt from an Azure ML job.

        Returns
        -------
        Path
            Local path to best.pt
        """

        temp_dir = Path(
            tempfile.mkdtemp(prefix="openvisionai_model_")
        )

        try:

            self.client.jobs.download(
                name=job_name,
                download_path=str(temp_dir),
                output_name="outputs",
            )

            best_model = (
                temp_dir
                / "outputs"
                / "models"
                / "best.pt"
            )

            if not best_model.exists():

                raise FileNotFoundError(
                    "best.pt not found."
                )

            return best_model

        except Exception:

            shutil.rmtree(
                temp_dir,
                ignore_errors=True,
            )

            raise

    # ==========================================================
    # Register Model
    # ==========================================================

    def register_job_output(
        self,
        job_name: str,
        registered_name: str,
        description: str | None = None,
    ) -> AzureModel:

        best_model = self._download_best_model(
            job_name
        )

        try:

            model = Model(
                path=str(best_model),
                name=registered_name,
                description=description,
                type="custom_model",
            )

            registered = (
                self.client.models.create_or_update(
                    model
                )
            )

            return AzureModel(
                name=registered.name,
                version=str(registered.version),
                description=registered.description,
                created_at=registered.creation_context.created_time,
            )

        except HttpResponseError as ex:

            raise ModelRegistrationException(
                str(ex)
            ) from ex

    # ==========================================================
    # Get Model
    # ==========================================================

    def get_model(
        self,
        model_name: str,
        version: str,
    ) -> AzureModel:

        try:

            model = self.client.models.get(
                name=model_name,
                version=version,
            )

            return AzureModel(
                name=model.name,
                version=str(model.version),
                description=model.description,
                created_at=model.creation_context.created_time,
            )

        except ResourceNotFoundError as ex:

            raise ModelNotFoundException(
                f"Model '{model_name}:{version}' not found."
            ) from ex

    # ==========================================================
    # List Models
    # ==========================================================

    def list_models(
        self,
    ) -> list[AzureModel]:

        models = []

        for model in self.client.models.list():

            models.append(

                AzureModel(
                    name=model.name,
                    version=str(model.version),
                    description=model.description,
                    created_at=model.creation_context.created_time,
                )

            )

        return models

    # ==========================================================
    # Delete Model
    # ==========================================================

    def delete_model(
        self,
        model_name: str,
        version: str,
    ) -> None:

        try:

            self.client.models.archive(
                name=model_name,
                version=version,
            )

        except HttpResponseError as ex:

            raise ModelRegistrationException(
                str(ex)
            ) from ex