"""add manual update markers

Revision ID: 20260524_0007
Revises: 20260522_0006
Create Date: 2026-05-24
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260524_0007"
down_revision: str | None = "20260522_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


TABLES = [
    "projects",
    "lpr_profiles",
    "lpr_importance_factors",
    "survey_batches",
    "survey_questions",
    "survey_responses",
    "survey_answers",
    "comment_analysis",
    "project_goals",
    "project_kpis",
    "client_expectations",
    "project_barriers",
    "barrier_mitigation_plans",
    "communication_points",
    "ai_project_findings",
    "ai_recommendations",
]


def upgrade() -> None:
    for table_name in TABLES:
        op.add_column(table_name, sa.Column("updated_by", sa.String(length=128), nullable=True))


def downgrade() -> None:
    for table_name in reversed(TABLES):
        op.drop_column(table_name, "updated_by")
