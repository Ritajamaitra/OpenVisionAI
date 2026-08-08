"""
OpenVisionAI Configuration

Loads all application configuration from .env
using Pydantic Settings.
"""

from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

# ==========================================================
# Locate backend/.env
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """
    OpenVisionAI Settings
    """

    # ==========================================================
    # Application
    # ==========================================================

    app_name: str = Field(
        default="OpenVisionAI",
        alias="OPENVISIONAI_APP_NAME",
    )

    app_version: str = Field(
        default="1.0.0",
        alias="OPENVISIONAI_APP_VERSION",
    )

    environment: str = Field(
        default="development",
        alias="OPENVISIONAI_ENVIRONMENT",
    )

    debug: bool = Field(
        default=False,
        alias="OPENVISIONAI_DEBUG",
    )

    # ==========================================================
    # Database
    # ==========================================================

    db_server: str = Field(alias="OPENVISIONAI_DB_SERVER")

    db_port: int = Field(
        default=1433,
        alias="OPENVISIONAI_DB_PORT",
    )

    db_name: str = Field(alias="OPENVISIONAI_DB_NAME")

    db_username: str = Field(alias="OPENVISIONAI_DB_USERNAME")

    db_password: str = Field(alias="OPENVISIONAI_DB_PASSWORD")

    db_driver: str = Field(
        default="ODBC Driver 18 for SQL Server",
        alias="OPENVISIONAI_DB_DRIVER",
    )

    # ==========================================================
    # Azure ML
    # ==========================================================

    azure_subscription_id: str = Field(
        alias="OPENVISIONAI_AZURE_SUBSCRIPTION_ID",
    )

    azure_resource_group: str = Field(
        alias="OPENVISIONAI_AZURE_RESOURCE_GROUP",
    )

    azure_ml_workspace: str = Field(
        alias="OPENVISIONAI_AZURE_ML_WORKSPACE",
    )

    compute_cluster: str = Field(
        alias="OPENVISIONAI_COMPUTE_CLUSTER",
    )

    environment_name: str = Field(
        alias="OPENVISIONAI_ENVIRONMENT_NAME",
    )

    # ==========================================================
    # Storage
    # ==========================================================

    storage_account: str = Field(
        alias="OPENVISIONAI_STORAGE_ACCOUNT",
    )

    storage_connection_string: str = Field(
        alias="OPENVISIONAI_STORAGE_CONNECTION_STRING",
    )

    dataset_container: str = Field(
        alias="OPENVISIONAI_DATASET_CONTAINER",
    )

    model_container: str = Field(
        alias="OPENVISIONAI_MODEL_CONTAINER",
    )

    export_container: str = Field(
        alias="OPENVISIONAI_EXPORT_CONTAINER",
    )

    report_container: str = Field(
        alias="OPENVISIONAI_REPORT_CONTAINER",
    )

    artifact_container: str = Field(
        alias="OPENVISIONAI_ARTIFACT_CONTAINER",
    )

    # ==========================================================
    # Azure Identity
    # ==========================================================

    azure_tenant_id: str = Field(
        alias="OPENVISIONAI_AZURE_TENANT_ID",
    )

    azure_client_id: str = Field(
        alias="OPENVISIONAI_AZURE_CLIENT_ID",
    )

    azure_client_secret: str = Field(
        alias="OPENVISIONAI_AZURE_CLIENT_SECRET",
    )

    # ==========================================================
    # JWT
    # ==========================================================

    secret_key: str = Field(
        alias="OPENVISIONAI_SECRET_KEY",
    )

    algorithm: str = Field(
        default="HS256",
        alias="OPENVISIONAI_ALGORITHM",
    )

    access_token_expire_minutes: int = Field(
        default=60,
        alias="OPENVISIONAI_ACCESS_TOKEN_EXPIRE_MINUTES",
    )

    # ==========================================================
    # Azure Training
    # ==========================================================

    azure_training_code_path: str = Field(
        default="backend/azureml",
        alias="OPENVISIONAI_AZURE_TRAINING_CODE_PATH",
    )

    # ==========================================================
    # SQLAlchemy URL
    # ==========================================================

    @property
    def database_url(self) -> str:

        params = quote_plus(
            (
                f"DRIVER={{{self.db_driver}}};"
                f"SERVER={self.db_server},{self.db_port};"
                f"DATABASE={self.db_name};"
                f"UID={self.db_username};"
                f"PWD={self.db_password};"
                "Encrypt=yes;"
                "TrustServerCertificate=no;"
            )
        )

        return f"mssql+pyodbc:///?odbc_connect={params}"

    # ==========================================================
    # Storage URL
    # ==========================================================

    @property
    def storage_account_url(self) -> str:

        return (
            f"https://{self.storage_account}"
            ".blob.core.windows.net"
        )

    # ==========================================================
    # Pydantic
    # ==========================================================

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()