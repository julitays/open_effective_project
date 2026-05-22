"""add_cjm_external_ids

Revision ID: 20260522_0003
Revises: 20260522_0002
Create Date: 2026-05-22

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260522_0003"
down_revision: str | None = "20260522_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "projects",
        sa.Column(
            "external_project_id",
            sa.String(length=128),
            nullable=True,
            comment="External source project ID without a real client or brand name.",
        ),
    )
    op.add_column(
        "projects",
        sa.Column(
            "working_project_code",
            sa.String(length=128),
            nullable=True,
            comment="Working source code without a real client or brand name.",
        ),
    )
    op.create_index(
        "ix_projects_external_project_id",
        "projects",
        ["external_project_id"],
        unique=False,
    )
    op.create_index(
        "ix_projects_working_project_code",
        "projects",
        ["working_project_code"],
        unique=False,
    )
    op.add_column(
        "lpr_profiles",
        sa.Column(
            "external_lpr_id",
            sa.String(length=128),
            nullable=True,
            comment="External source LPR ID without personal data.",
        ),
    )
    op.create_index(
        "ix_lpr_profiles_external_lpr_id",
        "lpr_profiles",
        ["external_lpr_id"],
        unique=False,
    )
    op.add_column(
        "barrier_mitigation_plans",
        sa.Column("confirmation_status", sa.String(length=64), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("barrier_mitigation_plans", "confirmation_status")
    op.drop_index("ix_lpr_profiles_external_lpr_id", table_name="lpr_profiles")
    op.drop_column("lpr_profiles", "external_lpr_id")
    op.drop_index("ix_projects_working_project_code", table_name="projects")
    op.drop_index("ix_projects_external_project_id", table_name="projects")
    op.drop_column("projects", "working_project_code")
    op.drop_column("projects", "external_project_id")
