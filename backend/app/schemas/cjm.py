from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.project import CJMProjectPassport, SanitizedPatchModel


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
    source_text: str | None
    evidence_quote: str | None
    period_or_source: str | None
    confidence_level: str | None


class CJMLPR(BaseModel):
    lpr_code: str
    external_lpr_id: str | None
    role: str
    role_zone: str
    influence_level: str | None
    activity_status: str | None
    relationship_status: str | None
    evidence_basis: str | None
    manual_comment: str | None
    importance_factors: list[CJMLPRImportanceFactor]


class CJMBarrier(BaseModel):
    barrier_id: str | None
    barrier_code: str | None
    barrier_title: str
    barrier_type: str
    time_status: Literal["past", "current", "future", "repeated"]
    criticality: str
    status: str
    description: str | None
    relevance_status: str | None
    confidence_level: str | None
    linked_kpi_text: str | None
    related_lpr_code: str | None
    external_lpr_id: str | None
    related_importance_text: str | None
    source_type: str | None
    source_id: str | None
    source_text: str | None
    evidence_quote: str | None
    first_seen_period: str | None
    last_seen_period: str | None


class CJMExpectation(BaseModel):
    expectation_id: str | None
    expectation_code: str | None
    expectation_text: str
    expectation_type: str
    explicitness: Literal["explicit", "implicit", "unknown"]
    criticality: str
    relevance_status: str | None
    confidence_level: str | None
    linked_kpi_text: str | None
    related_lpr_code: str | None
    external_lpr_id: str | None
    related_importance_text: str | None
    source: str | None
    source_text: str | None
    evidence_quote: str | None


class CJMKPI(BaseModel):
    kpi_id: str
    kpi_code: str
    kpi_name: str
    metric_name: str
    kpi_type: str | None
    source_text: str | None
    relevance_status: str | None
    related_expectation_text: str | None
    related_barrier_text: str | None
    client_criticality: str | None
    comment: str | None
    requires_confirmation: str | None
    target_value: str | None
    current_value: str | None
    unit: str | None
    status: str


class CJMCommunicationPoint(BaseModel):
    communication_id: str | None
    communication_code: str | None
    client_side: str | None
    external_lpr_id: str | None
    open_side_role: str | None
    topic_type: str | None
    topic_text: str | None
    channel: str
    channel_type: str
    channel_text: str | None
    frequency: str | None
    criticality: str | None
    source_text: str | None
    relevance_status: str | None
    comment: str | None
    summary: str
    outcome: str | None
    cjm_stage: str | None


class CJMGoal(BaseModel):
    goal_id: str | None
    goal_code: str | None
    goal_owner: str | None
    goal_text: str
    goal_type: str | None
    priority: str | None
    related_kpi_or_criterion_text: str | None
    source_text: str | None
    relevance_status: str | None
    comment: str | None
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


class ProjectContextBlockRead(BaseModel):
    section_key: str
    block_code: str
    block_type: str | None
    title: str | None
    content: dict[str, object]
    display_order: int
    updated_at: datetime


class ProjectEffectivenessRead(BaseModel):
    cjm: CJMProjectRead
    context_blocks: list[ProjectContextBlockRead]


class ArchiveRequest(SanitizedPatchModel):
    archive_reason: str | None = None


class CJMGoalCreate(SanitizedPatchModel):
    goal_code: str | None = None
    goal_owner: str | None = None
    goal_type: str | None = None
    goal_text: str
    priority: str | None = None
    related_kpi_or_criterion_text: str | None = None
    source_text: str | None = "web"
    relevance_status: str | None = "actual"
    comment: str | None = None


class CJMLPRCreate(SanitizedPatchModel):
    lpr_code: str | None = None
    external_lpr_id: str | None = None
    role_zone: str
    influence_level: str | None = "unknown"
    activity_status: str | None = "active"
    relationship_status: str | None = "unknown"
    evidence_basis: str | None = None
    manual_comment: str | None = None


class CJMBarrierCreate(SanitizedPatchModel):
    barrier_code: str | None = None
    barrier_title: str
    barrier_type: str = "other"
    time_status: str = "current"
    description: str | None = None
    criticality: str = "unknown"
    related_lpr_code: str | None = None
    external_lpr_id: str | None = None
    related_importance_text: str | None = None
    linked_kpi_text: str | None = None
    source_text: str | None = "web"
    evidence_quote: str | None = None
    status: str = "open"
    relevance_status: str | None = "actual"
    confidence_level: str | None = "unknown"


class CJMExpectationCreate(SanitizedPatchModel):
    expectation_code: str | None = None
    expectation_text: str
    expectation_type: str = "other"
    explicitness: str = "unknown"
    criticality: str = "unknown"
    related_lpr_code: str | None = None
    external_lpr_id: str | None = None
    related_importance_text: str | None = None
    linked_kpi_text: str | None = None
    source_text: str | None = "web"
    evidence_quote: str | None = None
    relevance_status: str | None = "actual"
    confidence_level: str | None = "unknown"


class CJMKPICreate(SanitizedPatchModel):
    kpi_code: str | None = None
    kpi_name: str
    kpi_type: str | None = None
    source_text: str | None = "web"
    relevance_status: str | None = "actual"
    related_expectation_text: str | None = None
    related_barrier_text: str | None = None
    client_criticality: str | None = "unknown"
    requires_confirmation: str | None = "unknown"
    comment: str | None = None


class CJMCommunicationPointCreate(SanitizedPatchModel):
    communication_code: str | None = None
    client_side: str | None = None
    external_lpr_id: str | None = None
    open_side_role: str | None = None
    topic_text: str | None = None
    channel_text: str | None = None
    frequency: str | None = None
    criticality: str | None = "unknown"
    source_text: str | None = "web"
    relevance_status: str | None = "actual"
    comment: str | None = None


class ProjectContextBlockCreate(SanitizedPatchModel):
    section_key: str
    block_code: str | None = None
    block_type: str | None = None
    title: str | None = None
    content: dict[str, object]
    display_order: int = 0


class ProjectContextBlockPatch(SanitizedPatchModel):
    block_type: str | None = None
    title: str | None = None
    content: dict[str, object] | None = None
    display_order: int | None = None


class CJMGoalPatch(SanitizedPatchModel):
    goal_owner: str | None = None
    goal_type: str | None = None
    goal_text: str | None = None
    priority: str | None = None
    related_kpi_or_criterion_text: str | None = None
    relevance_status: str | None = None
    comment: str | None = None


class CJMLPRPatch(SanitizedPatchModel):
    external_lpr_id: str | None = None
    role_zone: str | None = None
    influence_level: str | None = None
    activity_status: str | None = None
    relationship_status: str | None = None
    evidence_basis: str | None = None
    manual_comment: str | None = None


class CJMBarrierPatch(SanitizedPatchModel):
    barrier_title: str | None = None
    barrier_type: str | None = None
    time_status: str | None = None
    description: str | None = None
    criticality: str | None = None
    related_importance_text: str | None = None
    linked_kpi_text: str | None = None
    source_text: str | None = None
    evidence_quote: str | None = None
    status: str | None = None
    relevance_status: str | None = None
    confidence_level: str | None = None


class CJMExpectationPatch(SanitizedPatchModel):
    expectation_text: str | None = None
    expectation_type: str | None = None
    explicitness: str | None = None
    criticality: str | None = None
    related_importance_text: str | None = None
    linked_kpi_text: str | None = None
    source_text: str | None = None
    evidence_quote: str | None = None
    relevance_status: str | None = None
    confidence_level: str | None = None


class CJMKPIPatch(SanitizedPatchModel):
    kpi_name: str | None = None
    kpi_type: str | None = None
    source_text: str | None = None
    relevance_status: str | None = None
    related_expectation_text: str | None = None
    related_barrier_text: str | None = None
    client_criticality: str | None = None
    requires_confirmation: str | None = None
    comment: str | None = None


class CJMCommunicationPointPatch(SanitizedPatchModel):
    client_side: str | None = None
    external_lpr_id: str | None = None
    open_side_role: str | None = None
    topic_text: str | None = None
    channel_text: str | None = None
    frequency: str | None = None
    criticality: str | None = None
    source_text: str | None = None
    relevance_status: str | None = None
    comment: str | None = None
