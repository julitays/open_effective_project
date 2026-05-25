"""web first context and archive

Revision ID: 20260525_0008
Revises: 20260524_0007
Create Date: 2026-05-25
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260525_0008"
down_revision: str | None = "20260524_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


ACTIVE_TABLES = [
    "projects",
    "lpr_profiles",
    "lpr_importance_factors",
    "project_goals",
    "project_kpis",
    "client_expectations",
    "project_barriers",
    "communication_points",
]


def upgrade() -> None:
    for table_name in ACTIVE_TABLES:
        op.add_column(table_name, sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True))
        op.add_column(table_name, sa.Column("archived_by", sa.String(length=128), nullable=True))
        op.add_column(table_name, sa.Column("archive_reason", sa.Text(), nullable=True))

    op.create_table(
        "project_context_blocks",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("section_key", sa.String(length=128), nullable=False),
        sa.Column("block_code", sa.String(length=128), nullable=False),
        sa.Column("block_type", sa.String(length=128), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_by", sa.String(length=128), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_by", sa.String(length=128), nullable=True),
        sa.Column("archive_reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "project_id",
            "section_key",
            "block_code",
            name="uq_project_context_blocks_project_section_code",
        ),
    )
    op.create_index(
        op.f("ix_project_context_blocks_project_id"),
        "project_context_blocks",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_context_blocks_section_key"),
        "project_context_blocks",
        ["section_key"],
        unique=False,
    )

    op.drop_table("ai_recommendations")
    op.drop_table("ai_project_findings")
    op.drop_table("barrier_mitigation_plans")
    op.drop_table("comment_analysis")
    op.drop_table("survey_answers")
    op.drop_table("survey_responses")
    op.drop_table("survey_questions")
    op.drop_table("survey_batches")


def downgrade() -> None:
    op.create_table(
        "survey_batches",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("batch_code", sa.String(length=64), nullable=False),
        sa.Column("survey_type", sa.String(length=64), nullable=False),
        sa.Column("collection_period", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_by", sa.String(length=128), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "batch_code", name="uq_survey_batches_project_batch_code"),
    )
    # The removed tables were MVP placeholders only. Downgrade restores the root
    # survey table so the migration chain can move backwards without recreating
    # historical placeholder data.
    op.drop_index(op.f("ix_project_context_blocks_section_key"), table_name="project_context_blocks")
    op.drop_index(op.f("ix_project_context_blocks_project_id"), table_name="project_context_blocks")
    op.drop_table("project_context_blocks")

    for table_name in reversed(ACTIVE_TABLES):
        op.drop_column(table_name, "archive_reason")
        op.drop_column(table_name, "archived_by")
        op.drop_column(table_name, "archived_at")
