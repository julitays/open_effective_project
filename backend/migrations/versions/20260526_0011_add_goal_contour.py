"""add goal contour field

Revision ID: 20260526_0011
Revises: 20260526_0010
Create Date: 2026-05-26 20:25:00
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260526_0011"
down_revision = "20260526_0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("project_goals", sa.Column("goal_contour", sa.String(length=64), nullable=True))

    # Backfill contour from legacy goal_type values where contour and type were mixed.
    op.execute(
        """
        UPDATE project_goals
        SET goal_contour = CASE
            WHEN lower(goal_type) IN ('open_internal', 'open', 'цель open', 'наша цель') THEN 'open'
            WHEN lower(goal_type) IN ('client_business', 'client', 'цель клиента', 'клиентская цель') THEN 'client'
            WHEN lower(goal_type) IN ('joint_project', 'joint', 'совместная цель', 'общая цель проекта') THEN 'joint'
            ELSE goal_contour
        END
        WHERE goal_contour IS NULL
        """
    )

    # If goal_type stored contour-only semantics, clear it to avoid mixing with business type.
    op.execute(
        """
        UPDATE project_goals
        SET goal_type = NULL
        WHERE lower(goal_type) IN (
            'open_internal', 'open', 'цель open', 'наша цель',
            'client_business', 'client', 'цель клиента', 'клиентская цель',
            'joint_project', 'joint', 'совместная цель', 'общая цель проекта'
        )
        """
    )

    # Fallback contour by owner text if still empty.
    op.execute(
        """
        UPDATE project_goals
        SET goal_contour = CASE
            WHEN lower(coalesce(goal_owner, '')) LIKE '%клиент%' THEN 'client'
            WHEN lower(coalesce(goal_owner, '')) LIKE '%open%' THEN 'open'
            ELSE 'open'
        END
        WHERE goal_contour IS NULL
        """
    )


def downgrade() -> None:
    op.drop_column("project_goals", "goal_contour")

