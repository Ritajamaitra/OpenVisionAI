from sqlalchemy import create_engine
from urllib.parse import quote_plus

from app.config.settings import settings

connection_string = (
    f"DRIVER={{{settings.DB_DRIVER}}};"
    f"SERVER={settings.DB_SERVER},{settings.DB_PORT};"
    f"DATABASE={settings.DB_NAME};"
    f"UID={settings.DB_USERNAME};"
    f"PWD={settings.DB_PASSWORD};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
)

DATABASE_URL = (
    f"mssql+pyodbc:///?odbc_connect={quote_plus(connection_string)}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)