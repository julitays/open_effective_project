"""single_project_code

Revision ID: 20260526_0010
Revises: 20260526_0009
Create Date: 2026-05-26

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260526_0010"
down_revision: str | None = "20260526_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE projects
        SET external_project_id = project_code
        WHERE external_project_id IS NULL OR btrim(external_project_id) = '';
        """
    )

    op.execute(
        """
        WITH duplicates AS (
            SELECT id,
                   external_project_id,
                   ROW_NUMBER() OVER (PARTITION BY external_project_id ORDER BY created_at, id) AS rn
            FROM projects
            WHERE archived_at IS NULL
        )
        UPDATE projects p
        SET external_project_id = p.external_project_id || '_' || (d.rn - 1)::text
        FROM duplicates d
        WHERE p.id = d.id
          AND d.rn > 1;
        """
    )

    op.drop_index("ix_projects_working_project_code", table_name="projects")
    op.drop_column("projects", "working_project_code")

    op.alter_column("projects", "external_project_id", existing_type=sa.String(length=128), nullable=False)
    op.drop_index("ix_projects_external_project_id", table_name="projects")
    op.create_index(
        "ux_projects_external_project_id",
        "projects",
        ["external_project_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ux_projects_external_project_id", table_name="projects")
    op.create_index(
        "ix_projects_external_project_id",
        "projects",
        ["external_project_id"],
        unique=False,
    )
    op.alter_column("projects", "external_project_id", existing_type=sa.String(length=128), nullable=True)

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
        "ix_projects_working_project_code",
        "projects",
        ["working_project_code"],
        unique=False,
    )
