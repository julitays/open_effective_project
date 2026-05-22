from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AIProjectFindingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    finding_type: str
    finding_title: str
    summary: str
    criticality: str
    evidence_summary: str | None
    created_at: datetime
    updated_at: datetime


class AIRecommendationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    finding_id: UUID | None
    recommendation_type: str
    recommendation_text: str
    priority: str | None
    status: str
    created_at: datetime
    updated_at: datetime
