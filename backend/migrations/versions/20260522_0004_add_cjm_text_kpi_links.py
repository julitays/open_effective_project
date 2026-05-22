"""add_cjm_text_kpi_links

Revision ID: 20260522_0004
Revises: 20260522_0003
Create Date: 2026-05-22

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260522_0004"
down_revision: str | None = "20260522_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "project_barriers",
        sa.Column(
            "linked_kpi_text",
            sa.Text(),
            nullable=True,
            comment="Free-text KPI or success-criterion link restored from CJM.",
        ),
    )
    op.add_column(
        "client_expectations",
        sa.Column(
            "linked_kpi_text",
            sa.Text(),
            nullable=True,
            comment="Free-text KPI or success-criterion link restored from CJM.",
        ),
    )


def downgrade() -> None:
    op.drop_column("client_expectations", "linked_kpi_text")
    op.drop_column("project_barriers", "linked_kpi_text")
