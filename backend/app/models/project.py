from __future__ import annotations

from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

# TODO: Move stabilized string classifiers and statuses to lookup tables after MVP.


class Project(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "projects"

    project_code: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
        comment="Anonymized project code such as project_001.",
    )
    external_project_id: Mapped[str | None] = mapped_column(
        String(128),
        index=True,
        nullable=True,
        comment="External source project ID without a real client or brand name.",
    )
    working_project_code: Mapped[str | None] = mapped_column(
        String(128),
        index=True,
        nullable=True,
        comment="Working source code without a real client or brand name.",
    )
    project_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    project_scale: Mapped[str | None] = mapped_column(String(64), nullable=True)
    known_regions: Mapped[str | None] = mapped_column(Text, nullable=True)
    primary_operational_model: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )
    additional_operational_contours: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="active")
    current_phase: Mapped[str | None] = mapped_column(String(128), nullable=True)
    start_date: Mapped[str | None] = mapped_column(String(128), nullable=True)
    short_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    lpr_profiles: Mapped[list["LPRProfile"]] = relationship(
        "LPRProfile",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    survey_batches: Mapped[list["SurveyBatch"]] = relationship(
        "SurveyBatch",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    goals: Mapped[list["ProjectGoal"]] = relationship(
        "ProjectGoal",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    kpis: Mapped[list["ProjectKPI"]] = relationship(
        "ProjectKPI",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    expectations: Mapped[list["ClientExpectation"]] = relationship(
        "ClientExpectation",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    barriers: Mapped[list["ProjectBarrier"]] = relationship(
        "ProjectBarrier",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    mitigation_plans: Mapped[list["BarrierMitigationPlan"]] = relationship(
        "BarrierMitigationPlan",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    communication_points: Mapped[list["CommunicationPoint"]] = relationship(
        "CommunicationPoint",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    ai_findings: Mapped[list["AIProjectFinding"]] = relationship(
        "AIProjectFinding",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    ai_recommendations: Mapped[list["AIRecommendation"]] = relationship(
        "AIRecommendation",
        back_populates="project",
        cascade="all, delete-orphan",
    )


class ProjectGoal(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "project_goals"
    __table_args__ = (
        UniqueConstraint("project_id", "source_id", name="uq_project_goals_project_source_id"),
    )

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    source_id: Mapped[str | None] = mapped_column(
        String(128),
        index=True,
        nullable=True,
        comment="Stable manual CJM Goal ID from Excel.",
    )
    goal_owner: Mapped[str | None] = mapped_column(String(128), nullable=True)
    goal_text: Mapped[str] = mapped_column(Text, nullable=False)
    goal_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    priority: Mapped[str | None] = mapped_column(String(64), nullable=True)
    success_criteria: Mapped[str | None] = mapped_column(Text, nullable=True)
    related_kpi_or_criterion_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    relevance_status: Mapped[str | None] = mapped_column(String(128), nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="open")

    project: Mapped[Project] = relationship("Project", back_populates="goals")


class ProjectKPI(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "project_kpis"

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    kpi_code: Mapped[str] = mapped_column(String(64), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(255), nullable=False)
    kpi_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    source_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    relevance_status: Mapped[str | None] = mapped_column(String(128), nullable=True)
    related_expectation_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    related_barrier_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    client_criticality: Mapped[str | None] = mapped_column(String(64), nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    requires_confirmation: Mapped[str | None] = mapped_column(String(128), nullable=True)
    target_value: Mapped[str | None] = mapped_column(String(128), nullable=True)
    current_value: Mapped[str | None] = mapped_column(String(128), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="tracked")

    project: Mapped[Project] = relationship("Project", back_populates="kpis")


class ClientExpectation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "client_expectations"
    __table_args__ = (
        CheckConstraint(
            "explicitness IN ('explicit', 'implicit', 'unknown')",
            name="ck_client_expectations_explicitness",
        ),
        UniqueConstraint(
            "project_id",
            "source_id",
            name="uq_client_expectations_project_source_id",
        ),
    )

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    source_id: Mapped[str | None] = mapped_column(
        String(128),
        index=True,
        nullable=True,
        comment="Stable manual CJM Expectation ID from Excel.",
    )
    expectation_text: Mapped[str] = mapped_column(Text, nullable=False)
    expectation_type: Mapped[str] = mapped_column(String(64), nullable=False)
    explicitness: Mapped[str] = mapped_column(String(16), nullable=False)
    criticality: Mapped[str] = mapped_column(String(64), nullable=False)
    how_to_check: Mapped[str | None] = mapped_column(Text, nullable=True)
    related_lpr_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    external_lpr_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    related_importance_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    linked_kpi_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Free-text KPI or success-criterion link restored from CJM.",
    )
    source_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_quote: Mapped[str | None] = mapped_column(Text, nullable=True)
    relevance_status: Mapped[str | None] = mapped_column(String(128), nullable=True)
    confidence_level: Mapped[str | None] = mapped_column(String(128), nullable=True)

    project: Mapped[Project] = relationship("Project", back_populates="expectations")
