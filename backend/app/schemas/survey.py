from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SurveyBatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    batch_code: str
    survey_type: str
    collection_period: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class SurveyQuestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    batch_id: UUID
    question_code: str
    question_text: str
    question_type: str
    created_at: datetime
    updated_at: datetime


class SurveyResponseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    batch_id: UUID
    lpr_id: UUID | None
    response_code: str
    respondent_role: str | None
    submitted_at: datetime | None
    created_at: datetime
    updated_at: datetime


class SurveyAnswerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    batch_id: UUID
    response_id: UUID
    question_id: UUID
    answer_value: str | None
    original_comment_text: str | None = Field(
        description="Client comment stored only after anonymization before upload.",
    )
    created_at: datetime
    updated_at: datetime


class CommentAnalysisRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    answer_id: UUID
    topic_type: str
    sentiment: str
    criticality: str
    is_repeated_theme: bool
    summary: str
    evidence_quote: str | None
    analysis_source: Literal["manual", "ai"]
    confidence_score: float | None
    created_at: datetime
    updated_at: datetime
