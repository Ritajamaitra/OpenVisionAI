from datetime import datetime
from sqlalchemy.orm import Session

from app.integrations.azureml.azure_ml import azure_ml
from app.integrations.azureml.contracts import DeploymentRequest
from app.models.user import User
from app.services.model_services import ModelService
from app.services.training_run_services import TrainingService


class DeploymentException(Exception):
    """Raised when deployment fails."""


class DeploymentService:
    DEFAULT_ENDPOINT_PREFIX = "openvisionai-yolo"
    DEFAULT_DEPLOYMENT_NAME = "blue"
    DEFAULT_INSTANCE_TYPE = "Standard_DS11_v2"
    DEFAULT_INSTANCE_COUNT = 1

    DEFAULT_INFERENCE_ENVIRONMENT = "openvisionai-yolo-inference"
    DEFAULT_INFERENCE_ENVIRONMENT_VERSION = "1"
    DEFAULT_SCORING_CODE = "azureml/inference"
    DEFAULT_SCORING_SCRIPT = "score.py"

    def __init__(self, db: Session):
        self.db = db
        self.model_service = ModelService()
        self.training_service = TrainingService(db)
        self.azure_deployments = azure_ml.deployments

    def deploy_model(
        self,
        model_id: int,
        current_user: User,
        endpoint_name: str | None = None,
        deployment_name: str | None = None,
        instance_type: str | None = None,
        instance_count: int | None = None,
    ):
        model = self.model_service.get_model(
            db=self.db,
            model_id=model_id,
            current_user=current_user,
        )

        if not model.name or not model.version:
            raise DeploymentException(
                "Only registered models with a name and version can be deployed."
            )

        endpoint_name = (
            endpoint_name or self.DEFAULT_ENDPOINT_PREFIX
        )
        deployment_name = (
            deployment_name or self.DEFAULT_DEPLOYMENT_NAME
        )
        instance_type = (
            instance_type or self.DEFAULT_INSTANCE_TYPE
        )
        instance_count = (
            instance_count or self.DEFAULT_INSTANCE_COUNT
        )

        try:
            endpoint = self.azure_deployments.create_endpoint(
                endpoint_name=endpoint_name,
                description=(
                    "OpenVisionAI managed online endpoint."
                ),
                auth_mode="key",
            )

            request = DeploymentRequest(
                endpoint_name=endpoint.name,
                deployment_name=deployment_name,
                model_name=model.name,
                model_version=str(model.version),
                instance_type=instance_type,
                instance_count=instance_count,
            )

            deployment = self.azure_deployments.deploy_model(
                request=request,
                environment_name=self.DEFAULT_INFERENCE_ENVIRONMENT,
                environment_version=self.DEFAULT_INFERENCE_ENVIRONMENT_VERSION,
                scoring_code_path=self.DEFAULT_SCORING_CODE,
                scoring_script=self.DEFAULT_SCORING_SCRIPT,
            )

        except Exception as exc:
            raise DeploymentException(
                f"Model deployment failed: {exc}"
            ) from exc

        # Keep the existing TrainingRun endpoint reference in sync.
        for run in self.training_service.completed_jobs():
            if (
                run.registered_model_name == model.name
                and str(run.registered_model_version)
                == str(model.version)
            ):
                from app.schemas.training_run import TrainingRunUpdate

                self.training_service.update_training_run(
                    azure_run_id=run.azure_run_id,
                    update=TrainingRunUpdate(
                        endpoint_name=deployment.endpoint_name
                    ),
                )
                break

        return self._deployment_response(
            model=model,
            endpoint=endpoint,
            deployment=deployment,
        )

    def list_user_deployments(
        self,
        current_user: User,
    ) -> list[dict]:
        management_models = (
            self.model_service.get_user_model_management(
                db=self.db,
                current_user=current_user,
            )
        )

        owned_models = {
            (
                row["name"],
                str(row["version"]),
            ): row
            for row in management_models
        }

        rows = []

        try:
            endpoints = self.azure_deployments.list_endpoints()
        except Exception as exc:
            raise DeploymentException(
                f"Could not list Azure ML endpoints: {exc}"
            ) from exc

        for endpoint in endpoints:
            try:
                deployments = (
                    self.azure_deployments.list_deployments(
                        endpoint.name
                    )
                )
            except Exception:
                continue

            for deployment in deployments:
                key = (
                    deployment.model_name,
                    str(deployment.model_version),
                )

                model = owned_models.get(key)

                if model is None:
                    continue

                rows.append(
                    {
                        "model_id": model["id"],
                        "model_name": model["name"],
                        "model_version": str(model["version"]),
                        "dataset_name": model["dataset_name"],
                        "endpoint_name": endpoint.name,
                        "deployment_name": deployment.deployment_name,
                        "deployment_status": (
                            deployment.provisioning_state
                        ),
                        "endpoint_status": (
                            endpoint.provisioning_state
                        ),
                        "endpoint_url": endpoint.scoring_uri,
                        "instance_type": deployment.instance_type,
                        "instance_count": deployment.instance_count,
                        "azure_model_reference": (
                            f"{deployment.model_name}:"
                            f"{deployment.model_version}"
                        ),
                        "created_at": model["created_at"],
                    }
                )

        return rows

    def get_endpoint(
        self,
        endpoint_name: str,
        current_user: User,
    ):
        rows = self.list_user_deployments(
            current_user=current_user
        )

        for row in rows:
            if row["endpoint_name"] == endpoint_name:
                return row

        raise PermissionError(
            "Endpoint not found or access denied."
        )

    def stop_endpoint(
        self,
        endpoint_name: str,
        current_user: User,
    ) -> None:
        # Ownership check before destructive Azure operation.
        self.get_endpoint(
            endpoint_name=endpoint_name,
            current_user=current_user,
        )

        try:
            self.azure_deployments.delete_endpoint(
                endpoint_name
            )
        except Exception as exc:
            raise DeploymentException(
                f"Could not stop endpoint '{endpoint_name}': {exc}"
            ) from exc

    @staticmethod
    def _deployment_response(
        model,
        endpoint,
        deployment,
    ) -> dict:
        return {
            "model_id": model.id,
            "model_name": model.name,
            "model_version": str(model.version),
            "dataset_name": None,
            "endpoint_name": deployment.endpoint_name,
            "deployment_name": deployment.deployment_name,
            "deployment_status": deployment.provisioning_state,
            "endpoint_status": endpoint.provisioning_state,
            "endpoint_url": endpoint.scoring_uri,
            "instance_type": deployment.instance_type,
            "instance_count": deployment.instance_count,
            "azure_model_reference": (
                f"{deployment.model_name}:{deployment.model_version}"
            ),
            "created_at": getattr(model, "created_at", None),
        }
