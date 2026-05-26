"""normalize project context storage

Revision ID: 20260526_0009
Revises: 20260525_0008
Create Date: 2026-05-26
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260526_0009"
down_revision: str | None = "20260525_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "project_passport_facts",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("section_key", sa.String(length=32), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_by", sa.String(length=128), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_by", sa.String(length=128), nullable=True),
        sa.Column("archive_reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "section_key IN ('header', 'overview', 'service')",
            name="ck_project_passport_facts_section_key",
        ),
    )
    op.create_index(op.f("ix_project_passport_facts_project_id"), "project_passport_facts", ["project_id"], unique=False)
    op.create_index(op.f("ix_project_passport_facts_section_key"), "project_passport_facts", ["section_key"], unique=False)

    op.create_table(
        "project_client_vision_items",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("value_text", sa.Text(), nullable=False),
        sa.Column("use_text", sa.Text(), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_by", sa.String(length=128), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_by", sa.String(length=128), nullable=True),
        sa.Column("archive_reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_project_client_vision_items_project_id"), "project_client_vision_items", ["project_id"], unique=False)

    op.create_table(
        "project_work_contours",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("contour_name", sa.String(length=255), nullable=False),
        sa.Column("owner_role", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_by", sa.String(length=128), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_by", sa.String(length=128), nullable=True),
        sa.Column("archive_reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_project_work_contours_project_id"), "project_work_contours", ["project_id"], unique=False)

    op.create_table(
        "project_history_events",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("year_label", sa.String(length=64), nullable=False),
        sa.Column("event_title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_by", sa.String(length=128), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_by", sa.String(length=128), nullable=True),
        sa.Column("archive_reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_project_history_events_project_id"), "project_history_events", ["project_id"], unique=False)

    op.create_table(
        "project_need_pyramid_items",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("side", sa.String(length=16), nullable=False),
        sa.Column("level_label", sa.String(length=128), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_by", sa.String(length=128), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_by", sa.String(length=128), nullable=True),
        sa.Column("archive_reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("side IN ('client', 'open')", name="ck_project_need_pyramid_items_side"),
    )
    op.create_index(op.f("ix_project_need_pyramid_items_project_id"), "project_need_pyramid_items", ["project_id"], unique=False)
    op.create_index(op.f("ix_project_need_pyramid_items_side"), "project_need_pyramid_items", ["side"], unique=False)

    op.create_table(
        "project_structure_members",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("side", sa.String(length=16), nullable=False),
        sa.Column("role_title", sa.String(length=255), nullable=False),
        sa.Column("person_label", sa.String(length=255), nullable=True),
        sa.Column("zone_text", sa.Text(), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_by", sa.String(length=128), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_by", sa.String(length=128), nullable=True),
        sa.Column("archive_reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("side IN ('client', 'open')", name="ck_project_structure_members_side"),
    )
    op.create_index(op.f("ix_project_structure_members_project_id"), "project_structure_members", ["project_id"], unique=False)
    op.create_index(op.f("ix_project_structure_members_side"), "project_structure_members", ["side"], unique=False)

    op.create_table(
        "project_competitors",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("side", sa.String(length=16), nullable=False),
        sa.Column("competitor_name", sa.String(length=255), nullable=False),
        sa.Column("strengths_text", sa.Text(), nullable=True),
        sa.Column("weaknesses_text", sa.Text(), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_by", sa.String(length=128), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_by", sa.String(length=128), nullable=True),
        sa.Column("archive_reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("side IN ('client', 'open')", name="ck_project_competitors_side"),
    )
    op.create_index(op.f("ix_project_competitors_project_id"), "project_competitors", ["project_id"], unique=False)
    op.create_index(op.f("ix_project_competitors_side"), "project_competitors", ["side"], unique=False)

    op.create_table(
        "project_swot_items",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("item_text", sa.Text(), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_by", sa.String(length=128), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_by", sa.String(length=128), nullable=True),
        sa.Column("archive_reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "category IN ('strengths', 'weaknesses', 'opportunities', 'threats')",
            name="ck_project_swot_items_category",
        ),
    )
    op.create_index(op.f("ix_project_swot_items_project_id"), "project_swot_items", ["project_id"], unique=False)
    op.create_index(op.f("ix_project_swot_items_category"), "project_swot_items", ["category"], unique=False)

    op.create_table(
        "project_interpretation_rules",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("applies_to", sa.String(length=255), nullable=True),
        sa.Column("rule_text", sa.Text(), nullable=False),
        sa.Column("example_text", sa.Text(), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_by", sa.String(length=128), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_by", sa.String(length=128), nullable=True),
        sa.Column("archive_reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_project_interpretation_rules_project_id"), "project_interpretation_rules", ["project_id"], unique=False)

    op.create_table(
        "project_risk_items",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("risk_title", sa.String(length=255), nullable=False),
        sa.Column("risk_type", sa.String(length=128), nullable=True),
        sa.Column("probability_level", sa.String(length=64), nullable=True),
        sa.Column("probability_basis", sa.Text(), nullable=True),
        sa.Column("impact_level", sa.String(length=64), nullable=True),
        sa.Column("impact_basis", sa.Text(), nullable=True),
        sa.Column("related_to_text", sa.Text(), nullable=True),
        sa.Column("early_signal_text", sa.Text(), nullable=True),
        sa.Column("control_action", sa.Text(), nullable=True),
        sa.Column("control_owner", sa.String(length=255), nullable=True),
        sa.Column("review_period", sa.String(length=255), nullable=True),
        sa.Column("source_text", sa.Text(), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_by", sa.String(length=128), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_by", sa.String(length=128), nullable=True),
        sa.Column("archive_reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_project_risk_items_project_id"), "project_risk_items", ["project_id"], unique=False)

    op.create_table(
        "project_summary_items",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("group_key", sa.String(length=64), nullable=False),
        sa.Column("item_text", sa.Text(), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_by", sa.String(length=128), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_by", sa.String(length=128), nullable=True),
        sa.Column("archive_reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "group_key IN ('critical_to_client', 'main_risks')",
            name="ck_project_summary_items_group_key",
        ),
    )
    op.create_index(op.f("ix_project_summary_items_project_id"), "project_summary_items", ["project_id"], unique=False)
    op.create_index(op.f("ix_project_summary_items_group_key"), "project_summary_items", ["group_key"], unique=False)

    op.create_table(
        "project_summary_states",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_by", sa.String(length=128), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_by", sa.String(length=128), nullable=True),
        sa.Column("archive_reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", name="uq_project_summary_states_project_id"),
    )
    op.create_index(op.f("ix_project_summary_states_project_id"), "project_summary_states", ["project_id"], unique=False)

    _migrate_project_context_blocks()

    op.drop_index(op.f("ix_project_context_blocks_section_key"), table_name="project_context_blocks")
    op.drop_index(op.f("ix_project_context_blocks_project_id"), table_name="project_context_blocks")
    op.drop_table("project_context_blocks")


def downgrade() -> None:
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
    op.create_index(op.f("ix_project_context_blocks_project_id"), "project_context_blocks", ["project_id"], unique=False)
    op.create_index(op.f("ix_project_context_blocks_section_key"), "project_context_blocks", ["section_key"], unique=False)

    op.drop_index(op.f("ix_project_summary_states_project_id"), table_name="project_summary_states")
    op.drop_table("project_summary_states")
    op.drop_index(op.f("ix_project_summary_items_group_key"), table_name="project_summary_items")
    op.drop_index(op.f("ix_project_summary_items_project_id"), table_name="project_summary_items")
    op.drop_table("project_summary_items")
    op.drop_index(op.f("ix_project_risk_items_project_id"), table_name="project_risk_items")
    op.drop_table("project_risk_items")
    op.drop_index(op.f("ix_project_interpretation_rules_project_id"), table_name="project_interpretation_rules")
    op.drop_table("project_interpretation_rules")
    op.drop_index(op.f("ix_project_swot_items_category"), table_name="project_swot_items")
    op.drop_index(op.f("ix_project_swot_items_project_id"), table_name="project_swot_items")
    op.drop_table("project_swot_items")
    op.drop_index(op.f("ix_project_competitors_side"), table_name="project_competitors")
    op.drop_index(op.f("ix_project_competitors_project_id"), table_name="project_competitors")
    op.drop_table("project_competitors")
    op.drop_index(op.f("ix_project_structure_members_side"), table_name="project_structure_members")
    op.drop_index(op.f("ix_project_structure_members_project_id"), table_name="project_structure_members")
    op.drop_table("project_structure_members")
    op.drop_index(op.f("ix_project_need_pyramid_items_side"), table_name="project_need_pyramid_items")
    op.drop_index(op.f("ix_project_need_pyramid_items_project_id"), table_name="project_need_pyramid_items")
    op.drop_table("project_need_pyramid_items")
    op.drop_index(op.f("ix_project_history_events_project_id"), table_name="project_history_events")
    op.drop_table("project_history_events")
    op.drop_index(op.f("ix_project_work_contours_project_id"), table_name="project_work_contours")
    op.drop_table("project_work_contours")
    op.drop_index(op.f("ix_project_client_vision_items_project_id"), table_name="project_client_vision_items")
    op.drop_table("project_client_vision_items")
    op.drop_index(op.f("ix_project_passport_facts_section_key"), table_name="project_passport_facts")
    op.drop_index(op.f("ix_project_passport_facts_project_id"), table_name="project_passport_facts")
    op.drop_table("project_passport_facts")


def _migrate_project_context_blocks() -> None:
    bind = op.get_bind()

    old_blocks = sa.table(
        "project_context_blocks",
        sa.column("project_id", sa.Uuid()),
        sa.column("section_key", sa.String()),
        sa.column("block_code", sa.String()),
        sa.column("title", sa.String()),
        sa.column("content", sa.JSON()),
        sa.column("display_order", sa.Integer()),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
        sa.column("updated_by", sa.String()),
    )

    passport_facts = sa.table(
        "project_passport_facts",
        sa.column("project_id", sa.Uuid()),
        sa.column("section_key", sa.String()),
        sa.column("label", sa.String()),
        sa.column("value", sa.Text()),
        sa.column("display_order", sa.Integer()),
        sa.column("id", sa.Uuid()),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
        sa.column("updated_by", sa.String()),
    )
    client_vision = sa.table(
        "project_client_vision_items",
        sa.column("project_id", sa.Uuid()),
        sa.column("title", sa.String()),
        sa.column("value_text", sa.Text()),
        sa.column("use_text", sa.Text()),
        sa.column("display_order", sa.Integer()),
        sa.column("id", sa.Uuid()),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
        sa.column("updated_by", sa.String()),
    )
    work_contours = sa.table(
        "project_work_contours",
        sa.column("project_id", sa.Uuid()),
        sa.column("contour_name", sa.String()),
        sa.column("owner_role", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("display_order", sa.Integer()),
        sa.column("id", sa.Uuid()),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
        sa.column("updated_by", sa.String()),
    )
    history_events = sa.table(
        "project_history_events",
        sa.column("project_id", sa.Uuid()),
        sa.column("year_label", sa.String()),
        sa.column("event_title", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("display_order", sa.Integer()),
        sa.column("id", sa.Uuid()),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
        sa.column("updated_by", sa.String()),
    )
    need_items = sa.table(
        "project_need_pyramid_items",
        sa.column("project_id", sa.Uuid()),
        sa.column("side", sa.String()),
        sa.column("level_label", sa.String()),
        sa.column("title", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("display_order", sa.Integer()),
        sa.column("id", sa.Uuid()),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
        sa.column("updated_by", sa.String()),
    )
    structure_members = sa.table(
        "project_structure_members",
        sa.column("project_id", sa.Uuid()),
        sa.column("side", sa.String()),
        sa.column("role_title", sa.String()),
        sa.column("person_label", sa.String()),
        sa.column("zone_text", sa.Text()),
        sa.column("display_order", sa.Integer()),
        sa.column("id", sa.Uuid()),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
        sa.column("updated_by", sa.String()),
    )
    competitors = sa.table(
        "project_competitors",
        sa.column("project_id", sa.Uuid()),
        sa.column("side", sa.String()),
        sa.column("competitor_name", sa.String()),
        sa.column("strengths_text", sa.Text()),
        sa.column("weaknesses_text", sa.Text()),
        sa.column("display_order", sa.Integer()),
        sa.column("id", sa.Uuid()),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
        sa.column("updated_by", sa.String()),
    )
    swot_items = sa.table(
        "project_swot_items",
        sa.column("project_id", sa.Uuid()),
        sa.column("category", sa.String()),
        sa.column("item_text", sa.Text()),
        sa.column("display_order", sa.Integer()),
        sa.column("id", sa.Uuid()),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
        sa.column("updated_by", sa.String()),
    )
    interpretation_rules = sa.table(
        "project_interpretation_rules",
        sa.column("project_id", sa.Uuid()),
        sa.column("title", sa.String()),
        sa.column("applies_to", sa.String()),
        sa.column("rule_text", sa.Text()),
        sa.column("example_text", sa.Text()),
        sa.column("display_order", sa.Integer()),
        sa.column("id", sa.Uuid()),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
        sa.column("updated_by", sa.String()),
    )
    risk_items = sa.table(
        "project_risk_items",
        sa.column("project_id", sa.Uuid()),
        sa.column("risk_title", sa.String()),
        sa.column("risk_type", sa.String()),
        sa.column("probability_level", sa.String()),
        sa.column("probability_basis", sa.Text()),
        sa.column("impact_level", sa.String()),
        sa.column("impact_basis", sa.Text()),
        sa.column("related_to_text", sa.Text()),
        sa.column("early_signal_text", sa.Text()),
        sa.column("control_action", sa.Text()),
        sa.column("control_owner", sa.String()),
        sa.column("review_period", sa.String()),
        sa.column("source_text", sa.Text()),
        sa.column("display_order", sa.Integer()),
        sa.column("id", sa.Uuid()),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
        sa.column("updated_by", sa.String()),
    )
    summary_items = sa.table(
        "project_summary_items",
        sa.column("project_id", sa.Uuid()),
        sa.column("group_key", sa.String()),
        sa.column("item_text", sa.Text()),
        sa.column("display_order", sa.Integer()),
        sa.column("id", sa.Uuid()),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
        sa.column("updated_by", sa.String()),
    )
    summary_states = sa.table(
        "project_summary_states",
        sa.column("project_id", sa.Uuid()),
        sa.column("title", sa.String()),
        sa.column("note", sa.Text()),
        sa.column("id", sa.Uuid()),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
        sa.column("updated_by", sa.String()),
    )

    rows = bind.execute(
        sa.select(old_blocks).order_by(old_blocks.c.section_key, old_blocks.c.display_order)
    ).mappings().all()

    passport_map = {
        "passport_header": "header",
        "passport_overview": "overview",
        "passport_service": "service",
    }
    side_map = {
        "client_needs": "client",
        "open_needs": "open",
        "open_structure": "open",
        "client_structure": "client",
        "competitors_open": "open",
        "competitors_client": "client",
    }

    for row in rows:
        section = row["section_key"]
        content = row["content"] or {}
        common = {
            "project_id": row["project_id"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "updated_by": row["updated_by"],
        }

        if section in passport_map:
            for index, item in enumerate(_record_items(content)):
                label = _text(item.get("label"))
                value = _text(item.get("value"))
                if not label or not value:
                    continue
                bind.execute(
                    passport_facts.insert().values(
                        **common,
                        section_key=passport_map[section],
                        label=label,
                        value=value,
                        display_order=index,
                        id=sa.text("gen_random_uuid()"),
                    )
                )
        elif section == "client_vision":
            for index, item in enumerate(_record_items(content)):
                title = _text(item.get("title"))
                value = _text(item.get("value"))
                if not title or not value:
                    continue
                bind.execute(
                    client_vision.insert().values(
                        **common,
                        title=title,
                        value_text=value,
                        use_text=_text(item.get("use")),
                        display_order=index,
                        id=sa.text("gen_random_uuid()"),
                    )
                )
        elif section == "work_contours":
            for index, item in enumerate(_record_items(content)):
                contour = _text(item.get("contour"))
                text = _text(item.get("text"))
                if not contour or not text:
                    continue
                bind.execute(
                    work_contours.insert().values(
                        **common,
                        contour_name=contour,
                        owner_role=_text(item.get("owner")),
                        description=text,
                        display_order=index,
                        id=sa.text("gen_random_uuid()"),
                    )
                )
        elif section == "project_history":
            for index, item in enumerate(_record_items(content)):
                year = _text(item.get("year"))
                title = _text(item.get("title"))
                if not year or not title:
                    continue
                bind.execute(
                    history_events.insert().values(
                        **common,
                        year_label=year,
                        event_title=title,
                        description=_text(item.get("text")),
                        display_order=index,
                        id=sa.text("gen_random_uuid()"),
                    )
                )
        elif section in {"client_needs", "open_needs"}:
            for index, item in enumerate(_record_items(content)):
                level = _text(item.get("level"))
                title = _text(item.get("title"))
                if not level or not title:
                    continue
                bind.execute(
                    need_items.insert().values(
                        **common,
                        side=side_map[section],
                        level_label=level,
                        title=title,
                        description=_text(item.get("description")),
                        display_order=index,
                        id=sa.text("gen_random_uuid()"),
                    )
                )
        elif section in {"open_structure", "client_structure"}:
            for index, item in enumerate(_record_items(content)):
                role = _text(item.get("role"))
                if not role:
                    continue
                bind.execute(
                    structure_members.insert().values(
                        **common,
                        side=side_map[section],
                        role_title=role,
                        person_label=_text(item.get("person")),
                        zone_text=_text(item.get("zone")),
                        display_order=index,
                        id=sa.text("gen_random_uuid()"),
                    )
                )
        elif section in {"competitors_open", "competitors_client"}:
            for index, item in enumerate(_record_items(content)):
                name = _text(item.get("name"))
                if not name:
                    continue
                bind.execute(
                    competitors.insert().values(
                        **common,
                        side=side_map[section],
                        competitor_name=name,
                        strengths_text="\n".join(_string_list(item.get("strengths"))),
                        weaknesses_text="\n".join(_string_list(item.get("weaknesses"))),
                        display_order=index,
                        id=sa.text("gen_random_uuid()"),
                    )
                )
        elif section == "swot":
            for category in ("strengths", "weaknesses", "opportunities", "threats"):
                for index, text in enumerate(_string_list(content.get(category))):
                    bind.execute(
                        swot_items.insert().values(
                            **common,
                            category=category,
                            item_text=text,
                            display_order=index,
                            id=sa.text("gen_random_uuid()"),
                        )
                    )
        elif section == "interpretation_rules":
            items = _record_items(content)
            if items:
                for index, item in enumerate(items):
                    rule_text = _text(item.get("rule"))
                    if not rule_text:
                        continue
                    bind.execute(
                        interpretation_rules.insert().values(
                            **common,
                            title=_text(item.get("title")),
                            applies_to=_text(item.get("appliesTo") or item.get("applies_to")),
                            rule_text=rule_text,
                            example_text=_text(item.get("example")),
                            display_order=index,
                            id=sa.text("gen_random_uuid()"),
                        )
                    )
            else:
                for index, rule_text in enumerate(_string_list(content.get("rules"))):
                    bind.execute(
                        interpretation_rules.insert().values(
                            **common,
                            rule_text=rule_text,
                            display_order=index,
                            id=sa.text("gen_random_uuid()"),
                        )
                    )
        elif section == "risk_map":
            for index, item in enumerate(_record_items(content)):
                title = _text(item.get("title"))
                if not title:
                    continue
                bind.execute(
                    risk_items.insert().values(
                        **common,
                        risk_title=title,
                        risk_type=_text(item.get("barrier_type") or item.get("risk_type")),
                        probability_level=_text(item.get("probability_level")),
                        probability_basis=_text(item.get("probability_basis")),
                        impact_level=_text(item.get("impact_level")),
                        impact_basis=_text(item.get("impact_basis")),
                        related_to_text=_text(item.get("related_to")),
                        early_signal_text=_text(item.get("early_signal")),
                        control_action=_text(item.get("control_action")),
                        control_owner=_text(item.get("control_owner")),
                        review_period=_text(item.get("review_period")),
                        source_text=_text(item.get("source_text")),
                        display_order=index,
                        id=sa.text("gen_random_uuid()"),
                    )
                )
        elif section == "summary":
            bind.execute(
                summary_states.insert().values(
                    **common,
                    title=_text(row["title"]) or _text(content.get("title")),
                    note=_text(content.get("note")),
                    id=sa.text("gen_random_uuid()"),
                )
            )
            for group_key in ("critical_to_client", "main_risks"):
                for index, text in enumerate(_string_list(content.get(group_key))):
                    bind.execute(
                        summary_items.insert().values(
                            **common,
                            group_key=group_key,
                            item_text=text,
                            display_order=index,
                            id=sa.text("gen_random_uuid()"),
                        )
                    )


def _record_items(content: object) -> list[dict[str, object]]:
    if not isinstance(content, dict):
        return []
    items = content.get("items")
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict)]


def _string_list(value: object) -> list[str]:
    if isinstance(value, str):
        return [line.strip() for line in value.splitlines() if line.strip()]
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
