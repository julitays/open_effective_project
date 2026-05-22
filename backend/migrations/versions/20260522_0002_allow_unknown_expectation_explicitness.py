"""allow_unknown_expectation_explicitness

Revision ID: 20260522_0002
Revises: 20260522_0001
Create Date: 2026-05-22

"""
from collections.abc import Sequence

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "20260522_0002"
down_revision: str | None = "20260522_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        "ck_client_expectations_explicitness",
        "client_expectations",
        type_="check",
    )
    op.create_check_constraint(
        "ck_client_expectations_explicitness",
        "client_expectations",
        "explicitness IN ('explicit', 'implicit', 'unknown')",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_client_expectations_explicitness",
        "client_expectations",
        type_="check",
    )
    op.create_check_constraint(
        "ck_client_expectations_explicitness",
        "client_expectations",
        "explicitness IN ('explicit', 'implicit')",
    )
