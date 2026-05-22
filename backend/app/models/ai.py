from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

# TODO: Move stabilized string classifiers and statuses to lookup tables after MVP.


class AIProjectFinding(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "ai_project_findings"

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    finding_type: Mapped[str] = mapped_column(String(64), nullable=False)
    finding_title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    criticality: Mapped[str] = mapped_column(String(64), nullable=False)
    evidence_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="ai_findings")
    recommendations: Mapped[list["AIRecommendation"]] = relationship(
        "AIRecommendation",
        back_populates="finding",
    )


class AIRecommendation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "ai_recommendations"

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    finding_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("ai_project_findings.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    recommendation_type: Mapped[str] = mapped_column(String(64), nullable=False)
    recommendation_text: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="proposed")

    project: Mapped["Project"] = relationship("Project", back_populates="ai_recommendations")
    finding: Mapped[AIProjectFinding | None] = relationship(
        "AIProjectFinding",
        back_populates="recommendations",
    )
