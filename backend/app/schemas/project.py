from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SanitizedPatchModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @field_validator("*", mode="before")
    @classmethod
    def normalize_patch_value(cls, value: object) -> object:
        if not isinstance(value, str):
            return value

        trimmed = value.strip()
        if not trimmed or trimmed.lower() in {"null", "nan"}:
            return None
        return trimmed


class ProjectCreate(BaseModel):
    project_code: str = Field(pattern=r"^project_[A-Za-z0-9_-]+$")
    external_project_id: str | None = None
    working_project_code: str | None = None
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


class CJMProjectPassport(BaseModel):
    project_code: str
    external_project_id: str | None
    working_project_code: str | None
    direction: str | None
    project_scale: str | None
    known_regions: str | None
    primary_operational_model: str | None
    additional_operational_contours: str | None
    lifecycle_stage: str | None
    project_status: str
    start_date: str | None
    short_description: str | None
    updated_at: datetime


class CJMProjectPatch(SanitizedPatchModel):
    external_project_id: str | None = None
    working_project_code: str | None = None
    direction: str | None = None
    project_scale: str | None = None
    short_description: str | None = None
    known_regions: str | None = None
    primary_operational_model: str | None = None
    additional_operational_contours: str | None = None
    lifecycle_stage: str | None = None
    project_status: str | None = None
    start_date: str | None = None


class CJMProjectCreate(SanitizedPatchModel):
    project_code: str | None = Field(default=None, pattern=r"^project_[A-Za-z0-9_-]+$")
    external_project_id: str | None = None
    working_project_code: str | None = None
    direction: str | None = None
    project_scale: str | None = None
    known_regions: str | None = None
    primary_operational_model: str | None = None
    additional_operational_contours: str | None = None
    lifecycle_stage: str | None = None
    project_status: str = "active"
    start_date: str | None = None
    short_description: str | None = None
