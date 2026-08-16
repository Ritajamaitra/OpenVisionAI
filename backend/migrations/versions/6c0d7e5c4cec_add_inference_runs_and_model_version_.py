"""add inference runs and model version uniqueness

Revision ID: 6c0d7e5c4cec
Revises: f45db63d604e
Create Date: 2026-08-16 12:06:14.238482

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c0d7e5c4cec'
down_revision: Union[str, Sequence[str], None] = 'f45db63d604e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "inference_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("model_registry_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("model_version", sa.String(length=50), nullable=False),
        sa.Column("confidence_threshold", sa.Float(), nullable=False),
        sa.Column("prediction_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("predictions_json", sa.JSON(), nullable=True),
        sa.Column("inference_latency_ms", sa.Float(), nullable=True),
        sa.Column("input_filename", sa.String(length=255), nullable=True),
        sa.Column("input_content_type", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(
            ["model_registry_id"],
            ["model_registry.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_inference_runs_model_registry_id"),
        "inference_runs",
        ["model_registry_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_inference_runs_user_id"),
        "inference_runs",
        ["user_id"],
        unique=False,
    )
    op.create_unique_constraint(
        "uq_model_registry_version",
        "model_registry",
        ["name", "version"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "uq_model_registry_version",
        "model_registry",
        type_="unique",
    )
    op.drop_index(
        op.f("ix_inference_runs_user_id"),
        table_name="inference_runs",
    )
    op.drop_index(
        op.f("ix_inference_runs_model_registry_id"),
        table_name="inference_runs",
    )
    op.drop_table("inference_runs")
