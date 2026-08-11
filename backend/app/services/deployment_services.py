"""
OpenVisionAI Deployment Service

Responsibilities
----------------
1. Validate model ownership
2. Validate model status
3. Create Azure ML managed endpoint
4. Deploy registered model
5. Persist endpoint on the related training run
"""

from sqlalchemy.orm import Session

from app.integrations.azureml.azure_ml import azure_ml
from app.integrations.azureml.contracts import (
    DeploymentRequest,
)
from app.models.user import User
from app.services.model_services import ModelService
from app.services.training_run_services import (
    TrainingService,
)


class DeploymentException(Exception):
    """Raised when deployment fails."""


class DeploymentService:

    DEFAULT_ENDPOINT_PREFIX = (
        "openvisionai-yolo"
    )

    DEFAULT_DEPLOYMENT_NAME = "blue"

    DEFAULT_INSTANCE_TYPE = (
        "Standard_DS3_v2"
    )

    DEFAULT_INSTANCE_COUNT = 1

    DEFAULT_INFERENCE_ENVIRONMENT = (
        "openvisionai-yolo-inference"
    )

    DEFAULT_INFERENCE_ENVIRONMENT_VERSION = (
        "1"
    )

    DEFAULT_SCORING_CODE = (
        "azureml/inference"
    )

    DEFAULT_SCORING_SCRIPT = "score.py"

    def __init__(
        self,
        db: Session,
    ):

        self.db = db

        self.model_service = (
            ModelService()
        )

        self.training_service = (
            TrainingService(db)
        )

        self.azure_deployments = (
            azure_ml.deployments
        )

    # ======================================================
    # Deploy
    # ======================================================

    def deploy_model(
        self,
        model_id: int,
        current_user: User,
        endpoint_name: str | None = None,
        deployment_name: str | None = None,
        instance_type: str | None = None,
        instance_count: int | None = None,
    ):

        # --------------------------------------------------
        # 1. Validate model ownership
        # --------------------------------------------------

        model = self.model_service.get_model(
            db=self.db,
            model_id=model_id,
            current_user=current_user,
        )

        # --------------------------------------------------
        # 2. Validate model
        # --------------------------------------------------

        if not model.name:

            raise DeploymentException(
                "Registered model has no name."
            )

        if not model.version:

            raise DeploymentException(
                "Registered model has no version."
            )

        # --------------------------------------------------
        # 3. Resolve names
        # --------------------------------------------------

        endpoint_name = (
            endpoint_name
            or self.DEFAULT_ENDPOINT_PREFIX
        )

        deployment_name = (
            deployment_name
            or self.DEFAULT_DEPLOYMENT_NAME
        )

        instance_type = (
            instance_type
            or self.DEFAULT_INSTANCE_TYPE
        )

        instance_count = (
            instance_count
            or self.DEFAULT_INSTANCE_COUNT
        )

        # --------------------------------------------------
        # 4. Create / get endpoint
        # --------------------------------------------------

        try:

            endpoint = (
                self.azure_deployments
                .create_endpoint(
                    endpoint_name=endpoint_name,

                    description=(
                        "OpenVisionAI YOLO "
                        "object detection endpoint."
                    ),

                    auth_mode="key",
                )
            )

        except Exception as exc:

            raise DeploymentException(
                f"Endpoint creation failed: {exc}"
            ) from exc

        # --------------------------------------------------
        # 5. Build deployment request
        # --------------------------------------------------

        deployment_request = (
            DeploymentRequest(
                endpoint_name=endpoint.name,

                deployment_name=deployment_name,

                model_name=model.name,

                model_version=str(
                    model.version
                ),

                instance_type=instance_type,

                instance_count=instance_count,
            )
        )

        # --------------------------------------------------
        # 6. Deploy registered model
        # --------------------------------------------------

        try:

            deployment = (
                self.azure_deployments
                .deploy_model(
                    request=deployment_request,

                    environment_name=(
                        self
                        .DEFAULT_INFERENCE_ENVIRONMENT
                    ),

                    environment_version=(
                        self
                        .DEFAULT_INFERENCE_ENVIRONMENT_VERSION
                    ),

                    scoring_code_path=(
                        self.DEFAULT_SCORING_CODE
                    ),

                    scoring_script=(
                        self.DEFAULT_SCORING_SCRIPT
                    ),
                )
            )

        except Exception as exc:

            raise DeploymentException(
                f"Model deployment failed: {exc}"
            ) from exc

        # --------------------------------------------------
        # 7. Find related training run
        # --------------------------------------------------

        training_runs = (
            self.training_service
            .completed_jobs()
        )

        matching_run = None

        for run in training_runs:

            if (
                run.registered_model_name
                == model.name
                and
                str(
                    run.registered_model_version
                )
                == str(model.version)
            ):

                matching_run = run

                break

        # --------------------------------------------------
        # 8. Store endpoint name
        # --------------------------------------------------

        if matching_run:

            self.training_service.update_training_run(
                azure_run_id=(
                    matching_run.azure_run_id
                ),

                update=(
                    __import__(
                        "app.schemas.training_run",
                        fromlist=[
                            "TrainingRunUpdate"
                        ],
                    ).TrainingRunUpdate(
                        endpoint_name=(
                            deployment.endpoint_name
                        )
                    )
                ),
            )

        # --------------------------------------------------
        # 9. Return deployment result
        # --------------------------------------------------

        return {
            "model_id": model.id,

            "model_name": model.name,

            "model_version": str(
                model.version
            ),

            "endpoint_name": (
                deployment.endpoint_name
            ),

            "deployment_name": (
                deployment.deployment_name
            ),

            "deployment_status": (
                deployment.provisioning_state
            ),

            "scoring_uri": (
                endpoint.scoring_uri
            ),
        }

    # ======================================================
    # Get Endpoint
    # ======================================================

    def get_endpoint(
        self,
        endpoint_name: str,
    ):

        return (
            self.azure_deployments
            .get_endpoint(
                endpoint_name
            )
        )

    # ======================================================
    # List Endpoints
    # ======================================================

    def list_endpoints(self):

        return (
            self.azure_deployments
            .list_endpoints()
        )

    # ======================================================
    # Delete Endpoint
    # ======================================================

    def delete_endpoint(
        self,
        endpoint_name: str,
    ) -> None:

        self.azure_deployments.delete_endpoint(
            endpoint_name
        )