from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.project import CJMProjectPassport


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


class CJMLPRImportanceFactor(BaseModel):
    factor_type: str
    factor_text: str
    criticality: str | None
    source_type: str | None


class CJMLPR(BaseModel):
    lpr_code: str
    external_lpr_id: str | None
    role: str
    influence_level: str | None
    activity_status: str | None
    relationship_status: str | None
    importance_factors: list[CJMLPRImportanceFactor]


class CJMBarrier(BaseModel):
    barrier_id: str | None
    barrier_title: str
    barrier_type: str
    time_status: Literal["past", "current", "future", "repeated"]
    criticality: str
    status: str
    relevance_status: str | None
    confidence_level: str | None
    linked_kpi_text: str | None
    related_lpr_code: str | None
    source_type: str | None
    source_id: str | None
    evidence_quote: str | None


class CJMExpectation(BaseModel):
    expectation_id: str | None
    expectation_text: str
    expectation_type: str
    explicitness: Literal["explicit", "implicit", "unknown"]
    criticality: str
    relevance_status: str | None
    confidence_level: str | None
    linked_kpi_text: str | None
    related_lpr_code: str | None
    source: str | None
    evidence_quote: str | None


class CJMKPI(BaseModel):
    kpi_id: str
    metric_name: str
    target_value: str | None
    current_value: str | None
    unit: str | None
    status: str


class CJMCommunicationPoint(BaseModel):
    communication_id: str | None
    channel: str
    summary: str
    outcome: str | None
    cjm_stage: str | None


class CJMGoal(BaseModel):
    goal_id: str | None
    goal_text: str
    goal_type: str | None
    success_criteria: str | None
    status: str


class CJMProjectRead(BaseModel):
    project: CJMProjectPassport
    goals: list[CJMGoal]
    lprs: list[CJMLPR]
    barriers: list[CJMBarrier]
    expectations: list[CJMExpectation]
    kpis: list[CJMKPI]
    communications: list[CJMCommunicationPoint]
