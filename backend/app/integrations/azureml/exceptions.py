"""
OpenVisionAI Azure ML Exceptions

All Azure-specific exceptions should inherit from AzureMLException.
The rest of the application should never directly handle Azure SDK
exceptions.
"""


class AzureMLException(Exception):
    """
    Base exception for all Azure ML integration errors.
    """

    pass


# ==========================================================
# Workspace
# ==========================================================


class WorkspaceNotFoundException(AzureMLException):
    """
    Raised when the configured Azure ML workspace cannot be found.
    """

    pass


class WorkspaceConnectionException(AzureMLException):
    """
    Raised when Azure ML workspace connection fails.
    """

    pass


# ==========================================================
# Environment
# ==========================================================


class EnvironmentNotFoundException(AzureMLException):
    """
    Raised when an Azure ML environment cannot be found.
    """

    pass


class EnvironmentRegistrationException(AzureMLException):
    """
    Raised when an environment cannot be registered.
    """

    pass


# ==========================================================
# Training Jobs
# ==========================================================


class JobSubmissionException(AzureMLException):
    """
    Raised when Azure ML job submission fails.
    """

    pass


class JobNotFoundException(AzureMLException):
    """
    Raised when an Azure ML job does not exist.
    """

    pass


class JobCancellationException(AzureMLException):
    """
    Raised when cancelling a job fails.
    """

    pass


class JobMetricsException(AzureMLException):
    """
    Raised when training metrics cannot be retrieved.
    """

    pass


# ==========================================================
# Models
# ==========================================================


class ModelRegistrationException(AzureMLException):
    """
    Raised when model registration fails.
    """

    pass


class ModelNotFoundException(AzureMLException):
    """
    Raised when a registered model cannot be found.
    """

    pass


# ==========================================================
# Deployments
# ==========================================================


class EndpointNotFoundException(AzureMLException):
    """
    Raised when a managed endpoint cannot be found.
    """

    pass


class DeploymentException(AzureMLException):
    """
    Raised when deployment fails.
    """

    pass


# ==========================================================
# Datastores
# ==========================================================


class DatastoreNotFoundException(AzureMLException):
    """
    Raised when a datastore cannot be located.
    """

    pass


class DatasetUploadException(AzureMLException):
    """
    Raised when dataset upload to Azure ML fails.
    """

    pass