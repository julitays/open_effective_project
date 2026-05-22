"""add_cjm_readback_source_ids

Revision ID: 20260522_0005
Revises: 20260522_0004
Create Date: 2026-05-22

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260522_0005"
down_revision: str | None = "20260522_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "client_expectations",
        sa.Column(
            "source_id",
            sa.String(length=128),
            nullable=True,
            comment="Stable manual CJM Expectation ID from Excel.",
        ),
    )
    op.create_index(
        "ix_client_expectations_source_id",
        "client_expectations",
        ["source_id"],
        unique=False,
    )
    op.create_unique_constraint(
        "uq_client_expectations_project_source_id",
        "client_expectations",
        ["project_id", "source_id"],
    )

    op.add_column(
        "communication_points",
        sa.Column(
            "source_id",
            sa.String(length=128),
            nullable=True,
            comment="Stable manual CJM Communication ID from Excel.",
        ),
    )
    op.create_index(
        "ix_communication_points_source_id",
        "communication_points",
        ["source_id"],
        unique=False,
    )
    op.create_unique_constraint(
        "uq_communication_points_project_source_id",
        "communication_points",
        ["project_id", "source_id"],
    )

    op.add_column(
        "project_goals",
        sa.Column(
            "source_id",
            sa.String(length=128),
            nullable=True,
            comment="Stable manual CJM Goal ID from Excel.",
        ),
    )
    op.create_index(
        "ix_project_goals_source_id",
        "project_goals",
        ["source_id"],
        unique=False,
    )
    op.create_unique_constraint(
        "uq_project_goals_project_source_id",
        "project_goals",
        ["project_id", "source_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_project_goals_project_source_id",
        "project_goals",
        type_="unique",
    )
    op.drop_index("ix_project_goals_source_id", table_name="project_goals")
    op.drop_column("project_goals", "source_id")

    op.drop_constraint(
        "uq_communication_points_project_source_id",
        "communication_points",
        type_="unique",
    )
    op.drop_index("ix_communication_points_source_id", table_name="communication_points")
    op.drop_column("communication_points", "source_id")

    op.drop_constraint(
        "uq_client_expectations_project_source_id",
        "client_expectations",
        type_="unique",
    )
    op.drop_index("ix_client_expectations_source_id", table_name="client_expectations")
    op.drop_column("client_expectations", "source_id")
