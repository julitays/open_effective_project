from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LPRProfileCreate(BaseModel):
    project_id: UUID
    lpr_code: str = Field(pattern=r"^lpr_[A-Za-z0-9_-]+$")
    stakeholder_role: str
    influence_level: str | None = None
    engagement_status: str | None = None


class LPRProfileRead(LPRProfileCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class LPRImportanceFactorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    lpr_id: UUID
    factor_type: str
    factor_text: str
    importance_level: str | None
    source_type: str | None
    created_at: datetime
    updated_at: datetime
