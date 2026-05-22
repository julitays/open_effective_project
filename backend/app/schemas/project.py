from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    project_code: str = Field(pattern=r"^project_[A-Za-z0-9_-]+$")
    project_type: str | None = None
    status: str = "active"
    current_phase: str | None = None


class ProjectRead(ProjectCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class ProjectGoalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    goal_text: str
    goal_type: str | None
    success_criteria: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class ProjectKPIRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    kpi_code: str
    metric_name: str
    target_value: str | None
    current_value: str | None
    unit: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class ClientExpectationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    expectation_text: str
    expectation_type: str
    explicitness: Literal["explicit", "implicit", "unknown"]
    criticality: str
    how_to_check: str | None
    created_at: datetime
    updated_at: datetime
