"""complete_cjm_mvp_v6_fields

Revision ID: 20260522_0006
Revises: 20260522_0005
Create Date: 2026-05-22

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260522_0006"
down_revision: str | None = "20260522_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("projects", sa.Column("project_scale", sa.String(length=64), nullable=True))
    op.add_column("projects", sa.Column("known_regions", sa.Text(), nullable=True))
    op.add_column(
        "projects",
        sa.Column("primary_operational_model", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "projects",
        sa.Column("additional_operational_contours", sa.Text(), nullable=True),
    )
    op.add_column("projects", sa.Column("start_date", sa.String(length=128), nullable=True))
    op.add_column("projects", sa.Column("short_description", sa.Text(), nullable=True))

    op.add_column("lpr_profiles", sa.Column("activity_status", sa.String(length=128), nullable=True))
    op.add_column("lpr_profiles", sa.Column("relationship_status", sa.Text(), nullable=True))
    op.add_column("lpr_profiles", sa.Column("evidence_basis", sa.Text(), nullable=True))
    op.add_column("lpr_profiles", sa.Column("manual_comment", sa.Text(), nullable=True))

    op.add_column("lpr_importance_factors", sa.Column("source_text", sa.Text(), nullable=True))
    op.add_column("lpr_importance_factors", sa.Column("evidence_quote", sa.Text(), nullable=True))
    op.add_column("lpr_importance_factors", sa.Column("period_or_source", sa.Text(), nullable=True))
    op.add_column(
        "lpr_importance_factors",
        sa.Column("confidence_level", sa.String(length=128), nullable=True),
    )

    op.add_column("project_barriers", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("project_barriers", sa.Column("related_lpr_code", sa.Text(), nullable=True))
    op.add_column("project_barriers", sa.Column("external_lpr_id", sa.Text(), nullable=True))
    op.add_column(
        "project_barriers",
        sa.Column("related_importance_text", sa.Text(), nullable=True),
    )
    op.add_column("project_barriers", sa.Column("source_text", sa.Text(), nullable=True))
    op.add_column("project_barriers", sa.Column("evidence_quote", sa.Text(), nullable=True))
    op.add_column("project_barriers", sa.Column("first_seen_period", sa.Text(), nullable=True))
    op.add_column("project_barriers", sa.Column("last_seen_period", sa.Text(), nullable=True))
    op.add_column(
        "project_barriers",
        sa.Column("relevance_status", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "project_barriers",
        sa.Column("confidence_level", sa.String(length=128), nullable=True),
    )

    op.add_column("client_expectations", sa.Column("related_lpr_code", sa.Text(), nullable=True))
    op.add_column("client_expectations", sa.Column("external_lpr_id", sa.Text(), nullable=True))
    op.add_column(
        "client_expectations",
        sa.Column("related_importance_text", sa.Text(), nullable=True),
    )
    op.add_column("client_expectations", sa.Column("source_text", sa.Text(), nullable=True))
    op.add_column("client_expectations", sa.Column("evidence_quote", sa.Text(), nullable=True))
    op.add_column(
        "client_expectations",
        sa.Column("relevance_status", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "client_expectations",
        sa.Column("confidence_level", sa.String(length=128), nullable=True),
    )

    op.add_column("project_kpis", sa.Column("kpi_type", sa.String(length=128), nullable=True))
    op.add_column("project_kpis", sa.Column("source_text", sa.Text(), nullable=True))
    op.add_column(
        "project_kpis",
        sa.Column("relevance_status", sa.String(length=128), nullable=True),
    )
    op.add_column("project_kpis", sa.Column("related_expectation_text", sa.Text(), nullable=True))
    op.add_column("project_kpis", sa.Column("related_barrier_text", sa.Text(), nullable=True))
    op.add_column(
        "project_kpis",
        sa.Column("client_criticality", sa.String(length=64), nullable=True),
    )
    op.add_column("project_kpis", sa.Column("comment", sa.Text(), nullable=True))
    op.add_column(
        "project_kpis",
        sa.Column("requires_confirmation", sa.String(length=128), nullable=True),
    )

    op.add_column("communication_points", sa.Column("client_side", sa.Text(), nullable=True))
    op.add_column("communication_points", sa.Column("external_lpr_id", sa.Text(), nullable=True))
    op.add_column("communication_points", sa.Column("open_side_role", sa.Text(), nullable=True))
    op.add_column(
        "communication_points",
        sa.Column("topic_type", sa.String(length=128), nullable=True),
    )
    op.add_column("communication_points", sa.Column("topic_text", sa.Text(), nullable=True))
    op.add_column("communication_points", sa.Column("channel_text", sa.Text(), nullable=True))
    op.add_column("communication_points", sa.Column("frequency", sa.Text(), nullable=True))
    op.add_column(
        "communication_points",
        sa.Column("criticality", sa.String(length=64), nullable=True),
    )
    op.add_column("communication_points", sa.Column("source_text", sa.Text(), nullable=True))
    op.add_column(
        "communication_points",
        sa.Column("relevance_status", sa.String(length=128), nullable=True),
    )
    op.add_column("communication_points", sa.Column("comment", sa.Text(), nullable=True))

    op.add_column("project_goals", sa.Column("goal_owner", sa.String(length=128), nullable=True))
    op.add_column("project_goals", sa.Column("priority", sa.String(length=64), nullable=True))
    op.add_column(
        "project_goals",
        sa.Column("related_kpi_or_criterion_text", sa.Text(), nullable=True),
    )
    op.add_column("project_goals", sa.Column("source_text", sa.Text(), nullable=True))
    op.add_column(
        "project_goals",
        sa.Column("relevance_status", sa.String(length=128), nullable=True),
    )
    op.add_column("project_goals", sa.Column("comment", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("project_goals", "comment")
    op.drop_column("project_goals", "relevance_status")
    op.drop_column("project_goals", "source_text")
    op.drop_column("project_goals", "related_kpi_or_criterion_text")
    op.drop_column("project_goals", "priority")
    op.drop_column("project_goals", "goal_owner")

    op.drop_column("communication_points", "comment")
    op.drop_column("communication_points", "relevance_status")
    op.drop_column("communication_points", "source_text")
    op.drop_column("communication_points", "criticality")
    op.drop_column("communication_points", "frequency")
    op.drop_column("communication_points", "channel_text")
    op.drop_column("communication_points", "topic_text")
    op.drop_column("communication_points", "topic_type")
    op.drop_column("communication_points", "open_side_role")
    op.drop_column("communication_points", "external_lpr_id")
    op.drop_column("communication_points", "client_side")

    op.drop_column("project_kpis", "requires_confirmation")
    op.drop_column("project_kpis", "comment")
    op.drop_column("project_kpis", "client_criticality")
    op.drop_column("project_kpis", "related_barrier_text")
    op.drop_column("project_kpis", "related_expectation_text")
    op.drop_column("project_kpis", "relevance_status")
    op.drop_column("project_kpis", "source_text")
    op.drop_column("project_kpis", "kpi_type")

    op.drop_column("client_expectations", "confidence_level")
    op.drop_column("client_expectations", "relevance_status")
    op.drop_column("client_expectations", "evidence_quote")
    op.drop_column("client_expectations", "source_text")
    op.drop_column("client_expectations", "related_importance_text")
    op.drop_column("client_expectations", "external_lpr_id")
    op.drop_column("client_expectations", "related_lpr_code")

    op.drop_column("project_barriers", "confidence_level")
    op.drop_column("project_barriers", "relevance_status")
    op.drop_column("project_barriers", "last_seen_period")
    op.drop_column("project_barriers", "first_seen_period")
    op.drop_column("project_barriers", "evidence_quote")
    op.drop_column("project_barriers", "source_text")
    op.drop_column("project_barriers", "related_importance_text")
    op.drop_column("project_barriers", "external_lpr_id")
    op.drop_column("project_barriers", "related_lpr_code")
    op.drop_column("project_barriers", "description")

    op.drop_column("lpr_importance_factors", "confidence_level")
    op.drop_column("lpr_importance_factors", "period_or_source")
    op.drop_column("lpr_importance_factors", "evidence_quote")
    op.drop_column("lpr_importance_factors", "source_text")

    op.drop_column("lpr_profiles", "manual_comment")
    op.drop_column("lpr_profiles", "evidence_basis")
    op.drop_column("lpr_profiles", "relationship_status")
    op.drop_column("lpr_profiles", "activity_status")

    op.drop_column("projects", "short_description")
    op.drop_column("projects", "start_date")
    op.drop_column("projects", "additional_operational_contours")
    op.drop_column("projects", "primary_operational_model")
    op.drop_column("projects", "known_regions")
    op.drop_column("projects", "project_scale")
