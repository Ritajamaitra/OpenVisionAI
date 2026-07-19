from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore


class Settings(BaseSettings):
    APP_NAME: str = "OpenVisionAI"
    APP_VERSION: str = "0.1.0"
    ENV: str = "development"

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DB_SERVER: str
    DB_PORT: int = 1433
    DB_NAME: str
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_DRIVER: str
    DB_TRUST_CERTIFICATE: str = "no"

    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_prefix="OPENVISIONAI_",
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @property
    def database_url(self) -> str:
        connection_string = (
            f"DRIVER={{{self.DB_DRIVER}}};"
            f"SERVER={self.DB_SERVER},{self.DB_PORT};"
            f"DATABASE={self.DB_NAME};"
            f"UID={self.DB_USERNAME};"
            f"PWD={self.DB_PASSWORD};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
        )

        return (
            "mssql+pyodbc:///?odbc_connect="
            + quote_plus(connection_string)
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()