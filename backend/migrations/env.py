from logging.config import fileConfig

from sqlalchemy import create_engine
from alembic import context

from app.config.settings import settings
from app.models.base import BaseEntity

# Import ALL models
import app.models

config = context.config

config.set_main_option(
    "sqlalchemy.url",
    settings.database_url.replace("%", "%%"),
)

if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = BaseEntity.metadata


def run_migrations_offline():

    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():

    engine = create_engine(settings.database_url)

    with engine.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()