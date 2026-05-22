from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

# TODO: Move stabilized string classifiers and statuses to lookup tables after MVP.


class LPRProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lpr_profiles"
    __table_args__ = (
        UniqueConstraint("project_id", "lpr_code", name="uq_lpr_profiles_project_lpr_code"),
    )

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    lpr_code: Mapped[str] = mapped_column(
        String(64),
        index=True,
        nullable=False,
        comment="Anonymized decision-maker profile code such as lpr_001.",
    )
    external_lpr_id: Mapped[str | None] = mapped_column(
        String(128),
        index=True,
        nullable=True,
        comment="External source LPR ID without personal data.",
    )
    stakeholder_role: Mapped[str] = mapped_column(String(128), nullable=False)
    influence_level: Mapped[str | None] = mapped_column(String(64), nullable=True)
    engagement_status: Mapped[str | None] = mapped_column(String(64), nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="lpr_profiles")
    importance_factors: Mapped[list["LPRImportanceFactor"]] = relationship(
        "LPRImportanceFactor",
        back_populates="lpr",
        cascade="all, delete-orphan",
    )
    communication_points: Mapped[list["CommunicationPoint"]] = relationship(
        "CommunicationPoint",
        back_populates="lpr",
    )


class LPRImportanceFactor(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lpr_importance_factors"

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    lpr_id: Mapped[UUID] = mapped_column(
        ForeignKey("lpr_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    factor_type: Mapped[str] = mapped_column(String(64), nullable=False)
    factor_text: Mapped[str] = mapped_column(Text, nullable=False)
    importance_level: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(64), nullable=True)

    lpr: Mapped[LPRProfile] = relationship("LPRProfile", back_populates="importance_factors")
    project: Mapped["Project"] = relationship("Project")
