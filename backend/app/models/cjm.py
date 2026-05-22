from __future__ import annotations

from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

# TODO: Move stabilized string classifiers and statuses to lookup tables after MVP.


class ProjectBarrier(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "project_barriers"
    __table_args__ = (
        CheckConstraint(
            "time_status IN ('past', 'current', 'future', 'repeated')",
            name="ck_project_barriers_time_status",
        ),
    )

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    barrier_title: Mapped[str] = mapped_column(String(255), nullable=False)
    barrier_type: Mapped[str] = mapped_column(String(64), nullable=False)
    time_status: Mapped[str] = mapped_column(String(16), nullable=False)
    criticality: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(128), nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="barriers")
    mitigation_plans: Mapped[list["BarrierMitigationPlan"]] = relationship(
        "BarrierMitigationPlan",
        back_populates="barrier",
        cascade="all, delete-orphan",
    )


class CommunicationPoint(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "communication_points"

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    lpr_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("lpr_profiles.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    cjm_stage: Mapped[str | None] = mapped_column(String(128), nullable=True)
    point_type: Mapped[str] = mapped_column(String(64), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    outcome: Mapped[str | None] = mapped_column(Text, nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="communication_points")
    lpr: Mapped["LPRProfile | None"] = relationship(
        "LPRProfile",
        back_populates="communication_points",
    )
