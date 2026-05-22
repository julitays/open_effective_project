from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProjectBarrierRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    barrier_title: str
    barrier_type: str
    time_status: Literal["past", "current", "future", "repeated"]
    criticality: str
    status: str
    source_type: str
    source_id: str | None
    created_at: datetime
    updated_at: datetime


class CommunicationPointRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    lpr_id: UUID | None
    cjm_stage: str | None
    point_type: str
    summary: str
    outcome: str | None
    created_at: datetime
    updated_at: datetime
