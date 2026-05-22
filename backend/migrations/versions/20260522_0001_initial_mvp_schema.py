"""initial_mvp_schema

Revision ID: 20260522_0001
Revises:
Create Date: 2026-05-22

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260522_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("project_code", sa.String(length=64), nullable=False, comment="Anonymized project code such as project_001."),
        sa.Column("project_type", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("current_phase", sa.String(length=128), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_projects_project_code", "projects", ["project_code"], unique=True)

    op.create_table(
        "lpr_profiles",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column(
            "lpr_code",
            sa.String(length=64),
            nullable=False,
            comment="Anonymized decision-maker profile code such as lpr_001.",
        ),
        sa.Column("stakeholder_role", sa.String(length=128), nullable=False),
        sa.Column("influence_level", sa.String(length=64), nullable=True),
        sa.Column("engagement_status", sa.String(length=64), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "lpr_code", name="uq_lpr_profiles_project_lpr_code"),
    )
    op.create_index("ix_lpr_profiles_lpr_code", "lpr_profiles", ["lpr_code"], unique=False)
    op.create_index("ix_lpr_profiles_project_id", "lpr_profiles", ["project_id"], unique=False)

    op.create_table(
        "lpr_importance_factors",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("lpr_id", sa.Uuid(), nullable=False),
        sa.Column("factor_type", sa.String(length=64), nullable=False),
        sa.Column("factor_text", sa.Text(), nullable=False),
        sa.Column("importance_level", sa.String(length=64), nullable=True),
        sa.Column("source_type", sa.String(length=64), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["lpr_id"], ["lpr_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_lpr_importance_factors_lpr_id", "lpr_importance_factors", ["lpr_id"], unique=False)
    op.create_index("ix_lpr_importance_factors_project_id", "lpr_importance_factors", ["project_id"], unique=False)

    op.create_table(
        "survey_batches",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("batch_code", sa.String(length=64), nullable=False),
        sa.Column("survey_type", sa.String(length=64), nullable=False),
        sa.Column("collection_period", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "batch_code", name="uq_survey_batches_project_batch_code"),
    )
    op.create_index("ix_survey_batches_project_id", "survey_batches", ["project_id"], unique=False)

    op.create_table(
        "survey_questions",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("batch_id", sa.Uuid(), nullable=False),
        sa.Column("question_code", sa.String(length=64), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("question_type", sa.String(length=64), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["batch_id"], ["survey_batches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("batch_id", "question_code", name="uq_survey_questions_batch_question_code"),
    )
    op.create_index("ix_survey_questions_batch_id", "survey_questions", ["batch_id"], unique=False)
    op.create_index("ix_survey_questions_project_id", "survey_questions", ["project_id"], unique=False)

    op.create_table(
        "survey_responses",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("batch_id", sa.Uuid(), nullable=False),
        sa.Column("lpr_id", sa.Uuid(), nullable=True),
        sa.Column("response_code", sa.String(length=64), nullable=False),
        sa.Column("respondent_role", sa.String(length=128), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["batch_id"], ["survey_batches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["lpr_id"], ["lpr_profiles.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("batch_id", "response_code", name="uq_survey_responses_batch_response_code"),
    )
    op.create_index("ix_survey_responses_batch_id", "survey_responses", ["batch_id"], unique=False)
    op.create_index("ix_survey_responses_lpr_id", "survey_responses", ["lpr_id"], unique=False)
    op.create_index("ix_survey_responses_project_id", "survey_responses", ["project_id"], unique=False)

    op.create_table(
        "survey_answers",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("batch_id", sa.Uuid(), nullable=False),
        sa.Column("response_id", sa.Uuid(), nullable=False),
        sa.Column("question_id", sa.Uuid(), nullable=False),
        sa.Column("answer_value", sa.Text(), nullable=True),
        sa.Column(
            "original_comment_text",
            sa.Text(),
            nullable=True,
            comment="Original comment stored only after anonymization before MVP upload.",
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["batch_id"], ["survey_batches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["question_id"], ["survey_questions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["response_id"], ["survey_responses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_survey_answers_batch_id", "survey_answers", ["batch_id"], unique=False)
    op.create_index("ix_survey_answers_project_id", "survey_answers", ["project_id"], unique=False)
    op.create_index("ix_survey_answers_question_id", "survey_answers", ["question_id"], unique=False)
    op.create_index("ix_survey_answers_response_id", "survey_answers", ["response_id"], unique=False)

    op.create_table(
        "comment_analysis",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("answer_id", sa.Uuid(), nullable=False),
        sa.Column("topic_type", sa.String(length=64), nullable=False),
        sa.Column("sentiment", sa.String(length=64), nullable=False),
        sa.Column("criticality", sa.String(length=64), nullable=False),
        sa.Column("is_repeated_theme", sa.Boolean(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("evidence_quote", sa.Text(), nullable=True),
        sa.Column("analysis_source", sa.String(length=16), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("analysis_source IN ('manual', 'ai')", name="ck_comment_analysis_source"),
        sa.CheckConstraint(
            "confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)",
            name="ck_comment_analysis_confidence_score",
        ),
        sa.ForeignKeyConstraint(["answer_id"], ["survey_answers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_comment_analysis_answer_id", "comment_analysis", ["answer_id"], unique=False)
    op.create_index("ix_comment_analysis_project_id", "comment_analysis", ["project_id"], unique=False)

    op.create_table(
        "project_goals",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("goal_text", sa.Text(), nullable=False),
        sa.Column("goal_type", sa.String(length=64), nullable=True),
        sa.Column("success_criteria", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_project_goals_project_id", "project_goals", ["project_id"], unique=False)

    op.create_table(
        "project_kpis",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("kpi_code", sa.String(length=64), nullable=False),
        sa.Column("metric_name", sa.String(length=255), nullable=False),
        sa.Column("target_value", sa.String(length=128), nullable=True),
        sa.Column("current_value", sa.String(length=128), nullable=True),
        sa.Column("unit", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_project_kpis_project_id", "project_kpis", ["project_id"], unique=False)

    op.create_table(
        "client_expectations",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("expectation_text", sa.Text(), nullable=False),
        sa.Column("expectation_type", sa.String(length=64), nullable=False),
        sa.Column("explicitness", sa.String(length=16), nullable=False),
        sa.Column("criticality", sa.String(length=64), nullable=False),
        sa.Column("how_to_check", sa.Text(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "explicitness IN ('explicit', 'implicit')",
            name="ck_client_expectations_explicitness",
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_client_expectations_project_id", "client_expectations", ["project_id"], unique=False)

    op.create_table(
        "project_barriers",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("barrier_title", sa.String(length=255), nullable=False),
        sa.Column("barrier_type", sa.String(length=64), nullable=False),
        sa.Column("time_status", sa.String(length=16), nullable=False),
        sa.Column("criticality", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("source_id", sa.String(length=128), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "time_status IN ('past', 'current', 'future', 'repeated')",
            name="ck_project_barriers_time_status",
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_project_barriers_project_id", "project_barriers", ["project_id"], unique=False)

    op.create_table(
        "barrier_mitigation_plans",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("barrier_id", sa.Uuid(), nullable=False),
        sa.Column("action_type", sa.String(length=64), nullable=False),
        sa.Column("action_text", sa.Text(), nullable=False),
        sa.Column("owner_role", sa.String(length=128), nullable=False),
        sa.Column("due_period", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("check_method", sa.Text(), nullable=True),
        sa.Column("expected_effect", sa.Text(), nullable=True),
        sa.Column("actual_effect", sa.Text(), nullable=True),
        sa.Column("effect_status", sa.String(length=64), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["barrier_id"], ["project_barriers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_barrier_mitigation_plans_barrier_id", "barrier_mitigation_plans", ["barrier_id"], unique=False)
    op.create_index("ix_barrier_mitigation_plans_project_id", "barrier_mitigation_plans", ["project_id"], unique=False)

    op.create_table(
        "communication_points",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("lpr_id", sa.Uuid(), nullable=True),
        sa.Column("cjm_stage", sa.String(length=128), nullable=True),
        sa.Column("point_type", sa.String(length=64), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("outcome", sa.Text(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["lpr_id"], ["lpr_profiles.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_communication_points_lpr_id", "communication_points", ["lpr_id"], unique=False)
    op.create_index("ix_communication_points_project_id", "communication_points", ["project_id"], unique=False)

    op.create_table(
        "ai_project_findings",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("finding_type", sa.String(length=64), nullable=False),
        sa.Column("finding_title", sa.String(length=255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("criticality", sa.String(length=64), nullable=False),
        sa.Column("evidence_summary", sa.Text(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_project_findings_project_id", "ai_project_findings", ["project_id"], unique=False)

    op.create_table(
        "ai_recommendations",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("finding_id", sa.Uuid(), nullable=True),
        sa.Column("recommendation_type", sa.String(length=64), nullable=False),
        sa.Column("recommendation_text", sa.Text(), nullable=False),
        sa.Column("priority", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["finding_id"], ["ai_project_findings.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_recommendations_finding_id", "ai_recommendations", ["finding_id"], unique=False)
    op.create_index("ix_ai_recommendations_project_id", "ai_recommendations", ["project_id"], unique=False)


def downgrade() -> None:
    op.drop_table("ai_recommendations")
    op.drop_table("ai_project_findings")
    op.drop_table("communication_points")
    op.drop_table("barrier_mitigation_plans")
    op.drop_table("project_barriers")
    op.drop_table("client_expectations")
    op.drop_table("project_kpis")
    op.drop_table("project_goals")
    op.drop_table("comment_analysis")
    op.drop_table("survey_answers")
    op.drop_table("survey_responses")
    op.drop_table("survey_questions")
    op.drop_table("survey_batches")
    op.drop_table("lpr_importance_factors")
    op.drop_table("lpr_profiles")
    op.drop_table("projects")
