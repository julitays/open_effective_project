from __future__ import annotations

from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ProjectPassportFact(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "project_passport_facts"
    __table_args__ = (
        CheckConstraint(
            "section_key IN ('header', 'overview', 'service')",
            name="ck_project_passport_facts_section_key",
        ),
    )

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    section_key: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    display_order: Mapped[int] = mapped_column(nullable=False, default=0)

    project: Mapped["Project"] = relationship("Project", back_populates="passport_facts")


class ProjectClientVisionItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "project_client_vision_items"

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    value_text: Mapped[str] = mapped_column(Text, nullable=False)
    use_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(nullable=False, default=0)

    project: Mapped["Project"] = relationship("Project", back_populates="client_vision_items")


class ProjectWorkContour(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "project_work_contours"

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    contour_name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_role: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    display_order: Mapped[int] = mapped_column(nullable=False, default=0)

    project: Mapped["Project"] = relationship("Project", back_populates="work_contours")


class ProjectHistoryEvent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "project_history_events"

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    year_label: Mapped[str] = mapped_column(String(64), nullable=False)
    event_title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(nullable=False, default=0)

    project: Mapped["Project"] = relationship("Project", back_populates="history_events")


class ProjectNeedPyramidItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "project_need_pyramid_items"
    __table_args__ = (
        CheckConstraint(
            "side IN ('client', 'open')",
            name="ck_project_need_pyramid_items_side",
        ),
    )

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    side: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    level_label: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(nullable=False, default=0)

    project: Mapped["Project"] = relationship("Project", back_populates="need_pyramid_items")


class ProjectStructureMember(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "project_structure_members"
    __table_args__ = (
        CheckConstraint(
            "side IN ('client', 'open')",
            name="ck_project_structure_members_side",
        ),
    )

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    side: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    role_title: Mapped[str] = mapped_column(String(255), nullable=False)
    person_label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    zone_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(nullable=False, default=0)

    project: Mapped["Project"] = relationship("Project", back_populates="structure_members")


class ProjectCompetitor(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "project_competitors"
    __table_args__ = (
        CheckConstraint(
            "side IN ('client', 'open')",
            name="ck_project_competitors_side",
        ),
    )

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    side: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    competitor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    strengths_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    weaknesses_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(nullable=False, default=0)

    project: Mapped["Project"] = relationship("Project", back_populates="competitors")


class ProjectSwotItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "project_swot_items"
    __table_args__ = (
        CheckConstraint(
            "category IN ('strengths', 'weaknesses', 'opportunities', 'threats')",
            name="ck_project_swot_items_category",
        ),
    )

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    category: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    item_text: Mapped[str] = mapped_column(Text, nullable=False)
    display_order: Mapped[int] = mapped_column(nullable=False, default=0)

    project: Mapped["Project"] = relationship("Project", back_populates="swot_items")


class ProjectInterpretationRule(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "project_interpretation_rules"

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    applies_to: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rule_text: Mapped[str] = mapped_column(Text, nullable=False)
    example_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(nullable=False, default=0)

    project: Mapped["Project"] = relationship("Project", back_populates="interpretation_rules")


class ProjectRiskItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "project_risk_items"

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    risk_title: Mapped[str] = mapped_column(String(255), nullable=False)
    risk_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    probability_level: Mapped[str | None] = mapped_column(String(64), nullable=True)
    probability_basis: Mapped[str | None] = mapped_column(Text, nullable=True)
    impact_level: Mapped[str | None] = mapped_column(String(64), nullable=True)
    impact_basis: Mapped[str | None] = mapped_column(Text, nullable=True)
    related_to_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    early_signal_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    control_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    control_owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    review_period: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(nullable=False, default=0)

    project: Mapped["Project"] = relationship("Project", back_populates="risk_items")


class ProjectSummaryItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "project_summary_items"
    __table_args__ = (
        CheckConstraint(
            "group_key IN ('critical_to_client', 'main_risks')",
            name="ck_project_summary_items_group_key",
        ),
    )

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    group_key: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    item_text: Mapped[str] = mapped_column(Text, nullable=False)
    display_order: Mapped[int] = mapped_column(nullable=False, default=0)

    project: Mapped["Project"] = relationship("Project", back_populates="summary_items")


class ProjectSummaryState(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "project_summary_states"
    __table_args__ = (
        UniqueConstraint("project_id", name="uq_project_summary_states_project_id"),
    )

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="summary_state")
