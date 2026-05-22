from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

# TODO: Move stabilized string classifiers and statuses to lookup tables after MVP.


class BarrierMitigationPlan(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "barrier_mitigation_plans"

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    barrier_id: Mapped[UUID] = mapped_column(
        ForeignKey("project_barriers.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    action_type: Mapped[str] = mapped_column(String(64), nullable=False)
    action_text: Mapped[str] = mapped_column(Text, nullable=False)
    owner_role: Mapped[str] = mapped_column(String(128), nullable=False)
    due_period: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    confirmation_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    check_method: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_effect: Mapped[str | None] = mapped_column(Text, nullable=True)
    actual_effect: Mapped[str | None] = mapped_column(Text, nullable=True)
    effect_status: Mapped[str | None] = mapped_column(String(64), nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="mitigation_plans")
    barrier: Mapped["ProjectBarrier"] = relationship(
        "ProjectBarrier",
        back_populates="mitigation_plans",
    )
