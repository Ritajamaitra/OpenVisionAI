"""Initial database schema placeholder.

This revision is created so Alembic can resolve the head ID that already exists
in the database's alembic_version table. A fresh autogenerate migration can
then be created from the current SQLAlchemy models.
"""

from alembic import op

# revision identifiers used by Alembic.
revision = "7cf956d54f70"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """No-op placeholder for the existing database state."""
    pass


def downgrade() -> None:
    """No-op placeholder for the existing database state."""
    pass
