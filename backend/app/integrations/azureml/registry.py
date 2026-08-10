"""
OpenVisionAI Azure ML Model Registry Client

Responsibilities
----------------
1. Register trained models
2. Retrieve registered models
3. List registered models
4. Delete registered models

This module isolates Azure ML Model Registry SDK objects from
the rest of OpenVisionAI.
"""

import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from azure.ai.ml.entities import Model
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
)

from app.integrations.azureml.client import get_azure_ml_client
from app.integrations.azureml.contracts import AzureModel
from app.integrations.azureml.exceptions import (
    ModelNotFoundException,
    ModelRegistrationException,
)


class AzureRegistryClient:

    def __init__(self):
        self.client = get_azure_ml_client().client

    # ==========================================================
    # Helpers
    # ==========================================================

    @staticmethod
    def _created_at(model) -> Optional[datetime]:
        """
        Normalize the model creation timestamp across Azure ML
        SDK object variations.

        Azure ML SDK versions may expose the timestamp through
        different attributes, so never access created_time
        directly.
        """

        creation = getattr(
            model,
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
            model,
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
        model,
    ) -> AzureModel:
        """
        Convert an Azure ML Model into the OpenVisionAI
        AzureModel contract.
        """

        return AzureModel(
            name=model.name,
            version=str(model.version),
            description=getattr(
                model,
                "description",
                None,
            ),
            created_at=cls._created_at(model),
        )

    # ==========================================================
    # Download Best Model
    # ==========================================================

    def _download_best_model(
        self,
        job_name: str,
    ) -> tuple[Path, Path]:
        """
        Download outputs/models/best.pt from an Azure ML job.

        Returns
        -------
        tuple[Path, Path]
            (best_model_path, temporary_directory)
        """

        temp_dir = Path(
            tempfile.mkdtemp(
                prefix="openvisionai_model_"
            )
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
                    "Azure ML job output "
                    "'outputs/models/best.pt' was not found."
                )

            return best_model, temp_dir

        except Exception:
            shutil.rmtree(
                temp_dir,
                ignore_errors=True,
            )
            raise

    # ==========================================================
    # Register Job Output
    # ==========================================================

    def register_job_output(
        self,
        job_name: str,
        registered_name: str,
        description: str | None = None,
    ) -> AzureModel:
        """
        Download best.pt from a completed Azure ML job and
        register it in the Azure ML model registry.
        """

        best_model, temp_dir = self._download_best_model(
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

            return self._to_contract(
                registered
            )

        except HttpResponseError as ex:
            raise ModelRegistrationException(
                str(ex)
            ) from ex

        except Exception as ex:
            raise ModelRegistrationException(
                str(ex)
            ) from ex

        finally:
            shutil.rmtree(
                temp_dir,
                ignore_errors=True,
            )

    # ==========================================================
    # Get Model
    # ==========================================================

    def get_model(
        self,
        model_name: str,
        version: str,
    ) -> AzureModel:
        """
        Retrieve one registered model version.
        """

        try:
            model = self.client.models.get(
                name=model_name,
                version=version,
            )

            return self._to_contract(
                model
            )

        except ResourceNotFoundError as ex:
            raise ModelNotFoundException(
                f"Model '{model_name}:{version}' not found."
            ) from ex

        except HttpResponseError as ex:
            raise ModelRegistrationException(
                str(ex)
            ) from ex

    # ==========================================================
    # List Models
    # ==========================================================

    def list_models(
        self,
    ) -> list[AzureModel]:
        """
        Return all registered models.
        """

        models = []

        try:
            for model in self.client.models.list():
                models.append(
                    self._to_contract(
                        model
                    )
                )

            return models

        except HttpResponseError as ex:
            raise ModelRegistrationException(
                str(ex)
            ) from ex

    # ==========================================================
    # Delete Model
    # ==========================================================

    def delete_model(
        self,
        model_name: str,
        version: str,
    ) -> None:
        """
        Delete a specific registered model version.
        """

        try:
            self.client.models.archive(
                name=model_name,
                version=version,
            )

        except ResourceNotFoundError as ex:
            raise ModelNotFoundException(
                f"Model '{model_name}:{version}' not found."
            ) from ex

        except HttpResponseError as ex:
            raise ModelRegistrationException(
                str(ex)
            ) from ex