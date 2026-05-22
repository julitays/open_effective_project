from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

# TODO: Move stabilized string classifiers and statuses to lookup tables after MVP.


class SurveyBatch(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "survey_batches"
    __table_args__ = (
        UniqueConstraint("project_id", "batch_code", name="uq_survey_batches_project_batch_code"),
    )

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    batch_code: Mapped[str] = mapped_column(String(64), nullable=False)
    survey_type: Mapped[str] = mapped_column(String(64), nullable=False)
    collection_period: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="draft")

    project: Mapped["Project"] = relationship("Project", back_populates="survey_batches")
    questions: Mapped[list["SurveyQuestion"]] = relationship(
        "SurveyQuestion",
        back_populates="batch",
        cascade="all, delete-orphan",
    )
    responses: Mapped[list["SurveyResponse"]] = relationship(
        "SurveyResponse",
        back_populates="batch",
        cascade="all, delete-orphan",
    )
    answers: Mapped[list["SurveyAnswer"]] = relationship(
        "SurveyAnswer",
        back_populates="batch",
        cascade="all, delete-orphan",
    )


class SurveyQuestion(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "survey_questions"
    __table_args__ = (
        UniqueConstraint("batch_id", "question_code", name="uq_survey_questions_batch_question_code"),
    )

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    batch_id: Mapped[UUID] = mapped_column(
        ForeignKey("survey_batches.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    question_code: Mapped[str] = mapped_column(String(64), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(64), nullable=False)

    batch: Mapped[SurveyBatch] = relationship("SurveyBatch", back_populates="questions")
    project: Mapped["Project"] = relationship("Project")
    answers: Mapped[list["SurveyAnswer"]] = relationship(
        "SurveyAnswer",
        back_populates="question",
    )


class SurveyResponse(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "survey_responses"
    __table_args__ = (
        UniqueConstraint("batch_id", "response_code", name="uq_survey_responses_batch_response_code"),
    )

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    batch_id: Mapped[UUID] = mapped_column(
        ForeignKey("survey_batches.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    lpr_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("lpr_profiles.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    response_code: Mapped[str] = mapped_column(String(64), nullable=False)
    respondent_role: Mapped[str | None] = mapped_column(String(128), nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    batch: Mapped[SurveyBatch] = relationship("SurveyBatch", back_populates="responses")
    project: Mapped["Project"] = relationship("Project")
    lpr: Mapped["LPRProfile | None"] = relationship("LPRProfile")
    answers: Mapped[list["SurveyAnswer"]] = relationship(
        "SurveyAnswer",
        back_populates="response",
        cascade="all, delete-orphan",
    )


class SurveyAnswer(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "survey_answers"

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    batch_id: Mapped[UUID] = mapped_column(
        ForeignKey("survey_batches.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    response_id: Mapped[UUID] = mapped_column(
        ForeignKey("survey_responses.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    question_id: Mapped[UUID] = mapped_column(
        ForeignKey("survey_questions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    answer_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_comment_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Original comment stored only after anonymization before MVP upload.",
    )

    batch: Mapped[SurveyBatch] = relationship("SurveyBatch", back_populates="answers")
    response: Mapped[SurveyResponse] = relationship("SurveyResponse", back_populates="answers")
    question: Mapped[SurveyQuestion] = relationship("SurveyQuestion", back_populates="answers")
    project: Mapped["Project"] = relationship("Project")
    analyses: Mapped[list["CommentAnalysis"]] = relationship(
        "CommentAnalysis",
        back_populates="answer",
        cascade="all, delete-orphan",
    )


class CommentAnalysis(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "comment_analysis"
    __table_args__ = (
        CheckConstraint("analysis_source IN ('manual', 'ai')", name="ck_comment_analysis_source"),
        CheckConstraint(
            "confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)",
            name="ck_comment_analysis_confidence_score",
        ),
    )

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    answer_id: Mapped[UUID] = mapped_column(
        ForeignKey("survey_answers.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    topic_type: Mapped[str] = mapped_column(String(64), nullable=False)
    sentiment: Mapped[str] = mapped_column(String(64), nullable=False)
    criticality: Mapped[str] = mapped_column(String(64), nullable=False)
    is_repeated_theme: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_quote: Mapped[str | None] = mapped_column(Text, nullable=True)
    analysis_source: Mapped[str] = mapped_column(String(16), nullable=False)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    answer: Mapped[SurveyAnswer] = relationship("SurveyAnswer", back_populates="analyses")
    project: Mapped["Project"] = relationship("Project")
