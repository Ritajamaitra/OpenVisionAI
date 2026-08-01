from typing import Dict, Optional

from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    CommandJob,
    Environment,
    ManagedOnlineDeployment,
    ManagedOnlineEndpoint,
    Model,
)
from azure.identity import ClientSecretCredential

from app.config.settings import settings


class AzureMLService:

    def __init__(self):

        credential = ClientSecretCredential(
            tenant_id=settings.AZURE_TENANT_ID,
            client_id=settings.AZURE_CLIENT_ID,
            client_secret=settings.AZURE_CLIENT_SECRET,
        )

        self.ml_client = MLClient(
            credential=credential,
            subscription_id=settings.AZURE_SUBSCRIPTION_ID,
            resource_group_name=settings.AZURE_RESOURCE_GROUP,
            workspace_name=settings.AZURE_ML_WORKSPACE,
        )

    # ==========================================================
    # Jobs
    # ==========================================================

    def submit_training_job(
        self,
        job: CommandJob,
    ):

        return self.ml_client.jobs.create_or_update(job)

    def get_training_job(
        self,
        run_id: str,
    ):

        return self.ml_client.jobs.get(run_id)

    def list_training_jobs(self):

        return list(self.ml_client.jobs.list())

    def cancel_training_job(
        self,
        run_id: str,
    ):

        self.ml_client.jobs.cancel(run_id)

    # ==========================================================
    # Job Information
    # ==========================================================

    def get_job_status(
        self,
        run_id: str,
    ) -> str:

        job = self.get_training_job(run_id)

        return job.status

    def get_experiment_name(
        self,
        run_id: str,
    ) -> Optional[str]:

        job = self.get_training_job(run_id)

        return job.experiment_name

    def get_job_display_name(
        self,
        run_id: str,
    ) -> Optional[str]:

        job = self.get_training_job(run_id)

        return job.display_name

    # ==========================================================
    # Metrics
    # ==========================================================

    def get_job_metrics(
        self,
        run_id: str,
    ) -> Dict:

        """
        Reads metrics logged during training.

        Expected keys:

        precision
        recall
        map50
        map50_95
        training_time
        """

        job = self.get_training_job(run_id)

        metrics = {}

        if hasattr(job, "properties"):

            metrics = job.properties.get(
                "mlflow.metrics",
                {},
            )

        return metrics

    # ==========================================================
    # Outputs
    # ==========================================================

    def get_outputs(
        self,
        run_id: str,
    ):

        job = self.get_training_job(run_id)

        return job.outputs

    # ==========================================================
    # Model Registry
    # ==========================================================

    def register_model(
        self,
        model: Model,
    ):

        return self.ml_client.models.create_or_update(
            model
        )

    def get_registered_model(
        self,
        model_name: str,
        version: str,
    ):

        return self.ml_client.models.get(
            name=model_name,
            version=version,
        )

    def list_models(self):

        return list(
            self.ml_client.models.list()
        )

    # ==========================================================
    # Environment
    # ==========================================================

    def get_environment(
        self,
        name: str,
        version: str,
    ) -> Environment:

        return self.ml_client.environments.get(
            name=name,
            version=version,
        )

    # ==========================================================
    # Deployment
    # ==========================================================

    def create_endpoint(
        self,
        endpoint: ManagedOnlineEndpoint,
    ):

        poller = (
            self.ml_client.online_endpoints.begin_create_or_update(
                endpoint
            )
        )

        return poller.result()

    def create_deployment(
        self,
        deployment: ManagedOnlineDeployment,
    ):

        poller = (
            self.ml_client.online_deployments.begin_create_or_update(
                deployment
            )
        )

        return poller.result()

    def get_endpoint(
        self,
        endpoint_name: str,
    ):

        return self.ml_client.online_endpoints.get(
            endpoint_name
        )

    def delete_endpoint(
        self,
        endpoint_name: str,
    ):

        poller = (
            self.ml_client.online_endpoints.begin_delete(
                endpoint_name
            )
        )

        return poller.result()

    # ==========================================================
    # Inference
    # ==========================================================

    def invoke_endpoint(
        self,
        endpoint_name: str,
        deployment_name: str,
        request_file: str,
    ):

        return self.ml_client.online_endpoints.invoke(
            endpoint_name=endpoint_name,
            deployment_name=deployment_name,
            request_file=request_file,
        )

    # ==========================================================
    # Sync Helper
    # ==========================================================

    def sync_run(
        self,
        run_id: str,
    ) -> Dict:

        job = self.get_training_job(run_id)

        metrics = self.get_job_metrics(run_id)

        return {

            "azure_run_id": run_id,

            "status": job.status,

            "experiment_name": job.experiment_name,

            "display_name": job.display_name,

            "created_at": getattr(
                job,
                "creation_context",
                None,
            ),

            "metrics": metrics,

            "outputs": job.outputs,

        }