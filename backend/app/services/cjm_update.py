from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
import re
from typing import Any

from pydantic import BaseModel

from app.models.cjm import CommunicationPoint, ProjectBarrier
from app.models.lpr import LPRProfile
from app.models.project import ClientExpectation, Project, ProjectGoal, ProjectKPI
from app.repositories.cjm_update import CJMUpdateRepository
from app.schemas.cjm import (
    CJMBarrier,
    CJMBarrierCreate,
    CJMBarrierPatch,
    CJMCommunicationPoint,
    CJMCommunicationPointCreate,
    CJMCommunicationPointPatch,
    CJMExpectation,
    CJMExpectationCreate,
    CJMExpectationPatch,
    CJMGoal,
    CJMGoalCreate,
    CJMGoalPatch,
    CJMKPI,
    CJMKPICreate,
    CJMKPIPatch,
    CJMLPR,
    CJMLPRCreate,
    CJMLPRPatch,
    ProjectContextBlockCreate,
    ProjectContextBlockPatch,
    ProjectContextBlockRead,
)
from app.schemas.project import CJMProjectCreate, CJMProjectPassport, CJMProjectPatch
from app.services.cjm_read import CJMReadService
from app.services.project_context import ProjectContextService
from app.core import cjm_mappings


class CJMPatchValueError(ValueError):
    pass


Mapper = Callable[[object], str | None]


class CJMUpdateService:
    def __init__(
        self,
        repository: CJMUpdateRepository,
        read_service: CJMReadService,
    ) -> None:
        self.repository = repository
        self.read_service = read_service

    def create_project(self, payload: CJMProjectCreate, updated_by: str) -> CJMProjectPassport:
        external_project_id = payload.external_project_id.strip()
        if not external_project_id:
            raise CJMPatchValueError("Project code is required.")
        if self.repository.get_project_by_external_id(external_project_id) is not None:
            raise CJMPatchValueError(
                f"Project with code '{external_project_id}' already exists."
            )
        project_code = payload.project_code or self._next_code("project", self.repository.list_project_codes())
        project = Project(
            project_code=project_code,
            external_project_id=external_project_id,
            project_type=cjm_mappings.map_direction(payload.direction) or payload.direction,
            project_scale=cjm_mappings.map_project_scale(payload.project_scale) or payload.project_scale,
            known_regions=payload.known_regions,
            primary_operational_model=(
                cjm_mappings.map_operational_model(payload.primary_operational_model)
                or payload.primary_operational_model
            ),
            additional_operational_contours=payload.additional_operational_contours,
            current_phase=cjm_mappings.map_lifecycle_stage(payload.lifecycle_stage)
            or payload.lifecycle_stage,
            status=cjm_mappings.map_project_status(payload.project_status) or payload.project_status,
            start_date=payload.start_date,
            short_description=payload.short_description,
        )
        self._mark_manual_update(project, updated_by)
        self.repository.save(project)
        return self.read_service._project_passport(project)

    def create_goal(
        self,
        project_code: str,
        payload: CJMGoalCreate,
        updated_by: str,
    ) -> CJMGoal | None:
        project = self.repository.get_project(project_code)
        if project is None:
            return None
        goal_code = payload.goal_code or self._next_code(
            "goal",
            self.repository.list_codes(project.id, "goal"),
        )
        goal = ProjectGoal(
            project_id=project.id,
            source_id=goal_code,
            goal_owner=payload.goal_owner,
            goal_contour=map_goal_contour(payload.goal_contour) or payload.goal_contour,
            goal_text=payload.goal_text,
            goal_type=map_goal_type(payload.goal_type) or payload.goal_type,
            priority=map_priority(payload.priority) or payload.priority,
            related_kpi_or_criterion_text=payload.related_kpi_or_criterion_text,
            source_text=payload.source_text,
            relevance_status=map_relevance_status(payload.relevance_status)
            or payload.relevance_status,
            comment=payload.comment,
            status="open",
        )
        self._mark_manual_update(goal, updated_by)
        self.repository.save(goal)
        return self.read_service._goal(goal)

    def create_lpr(
        self,
        project_code: str,
        payload: CJMLPRCreate,
        updated_by: str,
    ) -> CJMLPR | None:
        project = self.repository.get_project(project_code)
        if project is None:
            return None
        lpr_code = payload.lpr_code or self._next_code(
            "lpr",
            self.repository.list_codes(project.id, "lpr"),
        )
        lpr = LPRProfile(
            project_id=project.id,
            lpr_code=lpr_code,
            external_lpr_id=payload.external_lpr_id,
            stakeholder_role=payload.role_zone,
            influence_level=map_influence_level(payload.influence_level) or payload.influence_level,
            engagement_status=map_activity_status(payload.activity_status) or payload.activity_status,
            activity_status=map_activity_status(payload.activity_status) or payload.activity_status,
            relationship_status=map_relationship_status(payload.relationship_status)
            or payload.relationship_status,
            evidence_basis=payload.evidence_basis,
            manual_comment=payload.manual_comment,
        )
        self._mark_manual_update(lpr, updated_by)
        self.repository.save(lpr)
        return self.read_service._lpr(lpr)

    def create_barrier(
        self,
        project_code: str,
        payload: CJMBarrierCreate,
        updated_by: str,
    ) -> CJMBarrier | None:
        project = self.repository.get_project(project_code)
        if project is None:
            return None
        barrier_code = payload.barrier_code or self._next_code(
            "barrier",
            self.repository.list_codes(project.id, "barrier"),
        )
        barrier = ProjectBarrier(
            project_id=project.id,
            source_id=barrier_code,
            barrier_title=payload.barrier_title,
            barrier_type=cjm_mappings.map_barrier_type(payload.barrier_type)
            or payload.barrier_type,
            time_status=cjm_mappings.map_barrier_time_status(payload.time_status)
            or payload.time_status,
            description=payload.description,
            criticality=cjm_mappings.map_criticality(payload.criticality) or payload.criticality,
            related_lpr_code=payload.related_lpr_code,
            external_lpr_id=payload.external_lpr_id,
            related_importance_text=payload.related_importance_text,
            linked_kpi_text=payload.linked_kpi_text,
            source_text=payload.source_text,
            evidence_quote=payload.evidence_quote,
            status=cjm_mappings.map_barrier_status(payload.status) or payload.status,
            source_type="web",
            relevance_status=map_relevance_status(payload.relevance_status)
            or payload.relevance_status,
            confidence_level=map_confidence_level(payload.confidence_level)
            or payload.confidence_level,
        )
        self._mark_manual_update(barrier, updated_by)
        self.repository.save(barrier)
        return self.read_service._barrier(barrier)

    def create_expectation(
        self,
        project_code: str,
        payload: CJMExpectationCreate,
        updated_by: str,
    ) -> CJMExpectation | None:
        project = self.repository.get_project(project_code)
        if project is None:
            return None
        expectation_code = payload.expectation_code or self._next_code(
            "expectation",
            self.repository.list_codes(project.id, "expectation"),
        )
        expectation = ClientExpectation(
            project_id=project.id,
            source_id=expectation_code,
            expectation_text=payload.expectation_text,
            expectation_type=cjm_mappings.map_expectation_type(payload.expectation_type)
            or payload.expectation_type,
            explicitness=cjm_mappings.map_explicitness(payload.explicitness)
            or payload.explicitness,
            criticality=cjm_mappings.map_criticality(payload.criticality) or payload.criticality,
            related_lpr_code=payload.related_lpr_code,
            external_lpr_id=payload.external_lpr_id,
            related_importance_text=payload.related_importance_text,
            linked_kpi_text=payload.linked_kpi_text,
            source_text=payload.source_text,
            evidence_quote=payload.evidence_quote,
            relevance_status=map_relevance_status(payload.relevance_status)
            or payload.relevance_status,
            confidence_level=map_confidence_level(payload.confidence_level)
            or payload.confidence_level,
        )
        self._mark_manual_update(expectation, updated_by)
        self.repository.save(expectation)
        return self.read_service._expectation(expectation)

    def create_kpi(
        self,
        project_code: str,
        payload: CJMKPICreate,
        updated_by: str,
    ) -> CJMKPI | None:
        project = self.repository.get_project(project_code)
        if project is None:
            return None
        kpi_code = payload.kpi_code or self._next_code(
            "kpi",
            self.repository.list_codes(project.id, "kpi"),
        )
        kpi = ProjectKPI(
            project_id=project.id,
            kpi_code=kpi_code,
            metric_name=payload.kpi_name,
            kpi_type=payload.kpi_type,
            source_text=payload.source_text,
            relevance_status=map_relevance_status(payload.relevance_status)
            or payload.relevance_status,
            related_expectation_text=payload.related_expectation_text,
            related_barrier_text=payload.related_barrier_text,
            client_criticality=cjm_mappings.map_criticality(payload.client_criticality)
            or payload.client_criticality,
            requires_confirmation=payload.requires_confirmation,
            comment=payload.comment,
            status="tracked",
        )
        self._mark_manual_update(kpi, updated_by)
        self.repository.save(kpi)
        return self.read_service._kpi(kpi)

    def create_communication(
        self,
        project_code: str,
        payload: CJMCommunicationPointCreate,
        updated_by: str,
    ) -> CJMCommunicationPoint | None:
        project = self.repository.get_project(project_code)
        if project is None:
            return None
        communication_code = payload.communication_code or self._next_code(
            "communication",
            self.repository.list_codes(project.id, "communication"),
        )
        summary = payload.topic_text or payload.comment or communication_code
        linked_lpr = self._resolve_lpr_for_communication(
            project.id,
            payload.external_lpr_id,
            payload.client_side,
        )
        point = CommunicationPoint(
            project_id=project.id,
            lpr_id=linked_lpr.id if linked_lpr is not None else None,
            source_id=communication_code,
            point_type="communication",
            client_side=payload.client_side,
            external_lpr_id=payload.external_lpr_id,
            open_side_role=payload.open_side_role,
            topic_text=payload.topic_text,
            channel_text=payload.channel_text,
            frequency=payload.frequency,
            criticality=cjm_mappings.map_criticality(payload.criticality)
            or payload.criticality,
            source_text=payload.source_text,
            relevance_status=map_relevance_status(payload.relevance_status)
            or payload.relevance_status,
            comment=payload.comment,
            summary=summary,
        )
        self._mark_manual_update(point, updated_by)
        self.repository.save(point)
        return self.read_service._communication(point)

    def create_context_block(
        self,
        project_code: str,
        payload: ProjectContextBlockCreate,
        updated_by: str,
    ) -> ProjectContextBlockRead | None:
        project = self.repository.get_project(project_code)
        if project is None:
            return None
        context_service = ProjectContextService(self.repository.session)
        return context_service.save_block(
            project,
            section_key=payload.section_key,
            block_code=payload.block_code or f"{payload.section_key}_001",
            block_type=payload.block_type,
            title=payload.title,
            content=payload.content,
            display_order=payload.display_order,
            updated_by=updated_by,
        )

    def update_context_block(
        self,
        project_code: str,
        section_key: str,
        block_code: str,
        patch: ProjectContextBlockPatch,
        updated_by: str,
    ) -> ProjectContextBlockRead | None:
        project = self.repository.get_project(project_code)
        if project is None:
            return None
        current = ProjectContextService(self.repository.session).get_block(project, section_key, block_code)
        if current is None:
            return None
        content = patch.content if patch.content is not None else current.content
        title = patch.title if patch.title is not None else current.title
        display_order = patch.display_order if patch.display_order is not None else current.display_order
        block_type = patch.block_type if patch.block_type is not None else current.block_type
        return ProjectContextService(self.repository.session).save_block(
            project,
            section_key=section_key,
            block_code=block_code,
            block_type=block_type,
            title=title,
            content=content,
            display_order=display_order,
            updated_by=updated_by,
        )

    def update_project(
        self,
        project_code: str,
        patch: CJMProjectPatch,
        updated_by: str,
    ) -> CJMProjectPassport | None:
        project = self.repository.get_project(project_code)
        if project is None:
            return None

        proposed_external_id = patch.external_project_id.strip() if patch.external_project_id else None
        if proposed_external_id:
            existing = self.repository.get_project_by_external_id(proposed_external_id)
            if existing is not None and existing.id != project.id:
                raise CJMPatchValueError(
                    f"Project with code '{proposed_external_id}' already exists."
                )

        self._apply_patch(
            project,
            patch,
            field_map={
                "direction": "project_type",
                "lifecycle_stage": "current_phase",
                "project_status": "status",
            },
            mappers={
                "direction": cjm_mappings.map_direction,
                "project_scale": cjm_mappings.map_project_scale,
                "primary_operational_model": cjm_mappings.map_operational_model,
                "lifecycle_stage": cjm_mappings.map_lifecycle_stage,
                "project_status": cjm_mappings.map_project_status,
            },
        )
        self._mark_manual_update(project, updated_by)
        self.repository.save(project)
        return self.read_service._project_passport(project)

    def update_goal(
        self,
        project_code: str,
        goal_code: str,
        patch: CJMGoalPatch,
        updated_by: str,
    ) -> CJMGoal | None:
        project = self.repository.get_project(project_code)
        if project is None:
            return None
        goal = self.repository.get_goal(project.id, goal_code)
        if goal is None:
            return None

        self._apply_patch(
            goal,
            patch,
            mappers={
                "goal_contour": map_goal_contour,
                "goal_type": map_goal_type,
                "relevance_status": map_relevance_status,
            },
        )
        self._mark_manual_update(goal, updated_by)
        self.repository.save(goal)
        return self.read_service._goal(goal)

    def update_lpr(
        self,
        project_code: str,
        lpr_code: str,
        patch: CJMLPRPatch,
        updated_by: str,
    ) -> CJMLPR | None:
        project = self.repository.get_project(project_code)
        if project is None:
            return None
        lpr = self.repository.get_lpr(project.id, lpr_code)
        if lpr is None:
            return None

        self._apply_patch(
            lpr,
            patch,
            field_map={"role_zone": "stakeholder_role"},
            mappers={
                "influence_level": map_influence_level,
                "activity_status": map_activity_status,
                "relationship_status": map_relationship_status,
            },
        )
        self._mark_manual_update(lpr, updated_by)
        self.repository.save(lpr)
        return self.read_service._lpr(lpr)

    def update_barrier(
        self,
        project_code: str,
        barrier_code: str,
        patch: CJMBarrierPatch,
        updated_by: str,
    ) -> CJMBarrier | None:
        project = self.repository.get_project(project_code)
        if project is None:
            return None
        barrier = self.repository.get_barrier(project.id, barrier_code)
        if barrier is None:
            return None

        self._apply_patch(
            barrier,
            patch,
            strict_mappers={
                "time_status": cjm_mappings.map_barrier_time_status,
            },
            mappers={
                "barrier_type": cjm_mappings.map_barrier_type,
                "criticality": cjm_mappings.map_criticality,
                "status": cjm_mappings.map_barrier_status,
                "relevance_status": map_relevance_status,
                "confidence_level": map_confidence_level,
            },
        )
        self._mark_manual_update(barrier, updated_by)
        self.repository.save(barrier)
        return self.read_service._barrier(barrier)

    def update_expectation(
        self,
        project_code: str,
        expectation_code: str,
        patch: CJMExpectationPatch,
        updated_by: str,
    ) -> CJMExpectation | None:
        project = self.repository.get_project(project_code)
        if project is None:
            return None
        expectation = self.repository.get_expectation(project.id, expectation_code)
        if expectation is None:
            return None

        self._apply_patch(
            expectation,
            patch,
            strict_mappers={"explicitness": cjm_mappings.map_explicitness},
            mappers={
                "expectation_type": cjm_mappings.map_expectation_type,
                "criticality": cjm_mappings.map_criticality,
                "relevance_status": map_relevance_status,
                "confidence_level": map_confidence_level,
            },
        )
        self._mark_manual_update(expectation, updated_by)
        self.repository.save(expectation)
        return self.read_service._expectation(expectation)

    def update_kpi(
        self,
        project_code: str,
        kpi_code: str,
        patch: CJMKPIPatch,
        updated_by: str,
    ) -> CJMKPI | None:
        project = self.repository.get_project(project_code)
        if project is None:
            return None
        kpi = self.repository.get_kpi(project.id, kpi_code)
        if kpi is None:
            return None

        self._apply_patch(
            kpi,
            patch,
            field_map={"kpi_name": "metric_name"},
            mappers={
                "client_criticality": cjm_mappings.map_criticality,
                "relevance_status": map_relevance_status,
            },
        )
        self._mark_manual_update(kpi, updated_by)
        self.repository.save(kpi)
        return self.read_service._kpi(kpi)

    def update_communication(
        self,
        project_code: str,
        communication_code: str,
        patch: CJMCommunicationPointPatch,
        updated_by: str,
    ) -> CJMCommunicationPoint | None:
        project = self.repository.get_project(project_code)
        if project is None:
            return None
        point = self.repository.get_communication(project.id, communication_code)
        if point is None:
            return None

        self._apply_patch(
            point,
            patch,
            mappers={
                "criticality": cjm_mappings.map_criticality,
                "relevance_status": map_relevance_status,
            },
        )
        linked_lpr = self._resolve_lpr_for_communication(
            project.id,
            point.external_lpr_id,
            point.client_side,
        )
        point.lpr_id = linked_lpr.id if linked_lpr is not None else None
        self._mark_manual_update(point, updated_by)
        self.repository.save(point)
        return self.read_service._communication(point)

    def archive_project(
        self,
        project_code: str,
        updated_by: str,
        archive_reason: str | None = None,
    ) -> CJMProjectPassport | None:
        project = self.repository.get_project(project_code)
        if project is None:
            return None
        self._archive(project, updated_by, archive_reason)
        self.repository.save(project)
        return self.read_service._project_passport(project)

    def archive_goal(
        self,
        project_code: str,
        goal_code: str,
        updated_by: str,
        archive_reason: str | None = None,
    ) -> CJMGoal | None:
        project = self.repository.get_project(project_code)
        if project is None:
            return None
        goal = self.repository.get_goal(project.id, goal_code)
        if goal is None:
            return None
        self._archive(goal, updated_by, archive_reason)
        self.repository.save(goal)
        return self.read_service._goal(goal)

    def archive_lpr(
        self,
        project_code: str,
        lpr_code: str,
        updated_by: str,
        archive_reason: str | None = None,
    ) -> CJMLPR | None:
        project = self.repository.get_project(project_code)
        if project is None:
            return None
        lpr = self.repository.get_lpr(project.id, lpr_code)
        if lpr is None:
            return None
        self._archive(lpr, updated_by, archive_reason)
        self.repository.save(lpr)
        return self.read_service._lpr(lpr)

    def archive_barrier(
        self,
        project_code: str,
        barrier_code: str,
        updated_by: str,
        archive_reason: str | None = None,
    ) -> CJMBarrier | None:
        project = self.repository.get_project(project_code)
        if project is None:
            return None
        barrier = self.repository.get_barrier(project.id, barrier_code)
        if barrier is None:
            return None
        self._archive(barrier, updated_by, archive_reason)
        self.repository.save(barrier)
        return self.read_service._barrier(barrier)

    def archive_expectation(
        self,
        project_code: str,
        expectation_code: str,
        updated_by: str,
        archive_reason: str | None = None,
    ) -> CJMExpectation | None:
        project = self.repository.get_project(project_code)
        if project is None:
            return None
        expectation = self.repository.get_expectation(project.id, expectation_code)
        if expectation is None:
            return None
        self._archive(expectation, updated_by, archive_reason)
        self.repository.save(expectation)
        return self.read_service._expectation(expectation)

    def archive_kpi(
        self,
        project_code: str,
        kpi_code: str,
        updated_by: str,
        archive_reason: str | None = None,
    ) -> CJMKPI | None:
        project = self.repository.get_project(project_code)
        if project is None:
            return None
        kpi = self.repository.get_kpi(project.id, kpi_code)
        if kpi is None:
            return None
        self._archive(kpi, updated_by, archive_reason)
        self.repository.save(kpi)
        return self.read_service._kpi(kpi)

    def archive_communication(
        self,
        project_code: str,
        communication_code: str,
        updated_by: str,
        archive_reason: str | None = None,
    ) -> CJMCommunicationPoint | None:
        project = self.repository.get_project(project_code)
        if project is None:
            return None
        point = self.repository.get_communication(project.id, communication_code)
        if point is None:
            return None
        self._archive(point, updated_by, archive_reason)
        self.repository.save(point)
        return self.read_service._communication(point)

    def _apply_patch(
        self,
        entity: object,
        patch: BaseModel,
        *,
        field_map: dict[str, str] | None = None,
        mappers: dict[str, Mapper] | None = None,
        strict_mappers: dict[str, Mapper] | None = None,
    ) -> None:
        field_map = field_map or {}
        mappers = mappers or {}
        strict_mappers = strict_mappers or {}
        values = patch.model_dump(exclude_unset=True)

        for api_field, raw_value in values.items():
            model_field = field_map.get(api_field, api_field)
            value = self._mapped_value(api_field, raw_value, mappers, strict_mappers)
            if value is None and not self._is_nullable(entity, model_field):
                continue
            setattr(entity, model_field, value)

    def _mapped_value(
        self,
        field_name: str,
        value: Any,
        mappers: dict[str, Mapper],
        strict_mappers: dict[str, Mapper],
    ) -> Any:
        if value is None:
            return None

        if field_name in strict_mappers:
            mapped = strict_mappers[field_name](value)
            if mapped is None:
                raise CJMPatchValueError(f"Unsupported value for '{field_name}': {value}")
            return mapped

        mapper = mappers.get(field_name)
        if mapper is None:
            return value

        return mapper(value) or value

    def _is_nullable(self, entity: object, field_name: str) -> bool:
        column = getattr(type(entity), field_name).property.columns[0]
        return bool(column.nullable)

    def _mark_manual_update(self, entity: object, updated_by: str) -> None:
        if hasattr(entity, "updated_by"):
            setattr(entity, "updated_by", updated_by)

    def _archive(self, entity: object, updated_by: str, archive_reason: str | None) -> None:
        if hasattr(entity, "archived_at"):
            setattr(entity, "archived_at", datetime.now(timezone.utc))
        if hasattr(entity, "archived_by"):
            setattr(entity, "archived_by", updated_by)
        if hasattr(entity, "archive_reason"):
            setattr(entity, "archive_reason", archive_reason)
        self._mark_manual_update(entity, updated_by)

    def _next_code(self, prefix: str, existing_codes: list[str]) -> str:
        existing = set(existing_codes)
        index = 1
        while True:
            candidate = f"{prefix}_{index:03d}"
            if candidate not in existing:
                return candidate
            index += 1

    def _resolve_lpr_for_communication(
        self,
        project_id: object,
        external_lpr_id: str | None,
        client_side: str | None,
    ) -> LPRProfile | None:
        lprs = self.repository.list_lprs(project_id)
        if not lprs:
            return None

        tokens = self._alias_tokens(external_lpr_id)
        if not tokens:
            tokens = self._alias_tokens(client_side)

        if tokens:
            for lpr in lprs:
                lpr_tokens = self._alias_tokens(lpr.external_lpr_id) | self._alias_tokens(lpr.lpr_code)
                if lpr_tokens & tokens:
                    return lpr

        client_side_normalized = cjm_mappings.normalize_label(client_side)
        if client_side_normalized:
            for lpr in lprs:
                role_normalized = cjm_mappings.normalize_label(lpr.stakeholder_role)
                if role_normalized and role_normalized == client_side_normalized:
                    return lpr
        return None

    def _alias_tokens(self, value: object) -> set[str]:
        normalized = cjm_mappings.normalize_label(value)
        if not normalized:
            return set()
        parts = re.split(r"[;,/|]+", normalized)
        return {part.strip() for part in parts if part.strip()}


def map_relevance_status(value: object) -> str | None:
    return _map_alias(
        value,
        {
            "actual": "actual",
            "current": "current",
            "актуально": "actual",
            "historical": "historical",
            "историческое": "historical",
            "requires_confirmation": "requires_confirmation",
            "требует подтверждения": "requires_confirmation",
            "not_actual": "not_actual",
            "неактуально": "not_actual",
            "unknown": "unknown",
            "не указано": "unknown",
        },
    )


def map_confidence_level(value: object) -> str | None:
    return _map_alias(
        value,
        {
            "high": "high",
            "высокая": "high",
            "высокий": "high",
            "высокая уверенность": "high",
            "medium": "medium",
            "средняя": "medium",
            "средний": "medium",
            "средняя уверенность": "medium",
            "low": "low",
            "низкая": "low",
            "низкий": "low",
            "низкая уверенность": "low",
            "unknown": "unknown",
            "не указано": "unknown",
        },
    )


def map_influence_level(value: object) -> str | None:
    return _map_alias(
        value,
        {
            "high": "high",
            "высокое": "high",
            "высокий": "high",
            "высокое влияние": "high",
            "medium": "medium",
            "среднее": "medium",
            "средний": "medium",
            "среднее влияние": "medium",
            "low": "low",
            "низкое": "low",
            "низкий": "low",
            "низкое влияние": "low",
            "requires_confirmation": "requires_confirmation",
            "требует подтверждения": "requires_confirmation",
            "unknown": "unknown",
            "не указано": "unknown",
        },
    )


def map_activity_status(value: object) -> str | None:
    return _map_alias(
        value,
        {
            "active": "active",
            "активен": "active",
            "inactive": "inactive",
            "неактивен": "inactive",
            "requires_confirmation": "requires_confirmation",
            "требует подтверждения": "requires_confirmation",
            "historical": "historical",
            "исторический": "historical",
            "unknown": "unknown",
            "не указано": "unknown",
        },
    )


def map_relationship_status(value: object) -> str | None:
    return _map_alias(
        value,
        {
            "loyal": "loyal",
            "лоялен": "loyal",
            "neutral": "neutral",
            "нейтрален": "neutral",
            "cautious": "cautious",
            "осторожен": "cautious",
            "critical": "critical",
            "критичен": "critical",
            "unknown": "unknown",
            "не указано": "unknown",
        },
    )


def map_goal_contour(value: object) -> str | None:
    return _map_alias(
        value,
        {
            "open": "open",
            "цель open": "open",
            "open цель": "open",
            "наша цель": "open",
            "клиент": "client",
            "цель клиента": "client",
            "клиентская цель": "client",
            "совместная": "joint",
            "совместная цель": "joint",
            "общая цель проекта": "joint",
            "joint": "joint",
            "unknown": "unknown",
            "не указано": "unknown",
        },
    )


def map_goal_type(value: object) -> str | None:
    return _map_alias(
        value,
        {
            "service": "service",
            "сервисная": "service",
            "сервисная цель": "service",
            "operational": "operational",
            "операционная": "operational",
            "операционная цель": "operational",
            "financial": "financial",
            "финансовая": "financial",
            "финансовая цель": "financial",
            "risk_control": "risk_control",
            "контроль рисков": "risk_control",
            "other": "other",
            "другое": "other",
            "unknown": "unknown",
            "не указано": "unknown",
        },
    )


def map_priority(value: object) -> str | None:
    return _map_alias(
        value,
        {
            "high": "high",
            "высокий": "high",
            "высокая": "high",
            "medium": "medium",
            "средний": "medium",
            "средняя": "medium",
            "low": "low",
            "низкий": "low",
            "низкая": "low",
            "unknown": "unknown",
            "не указано": "unknown",
        },
    )


def _map_alias(value: object, aliases: dict[str, str]) -> str | None:
    normalized = cjm_mappings.normalize_label(value)
    if not normalized:
        return None
    return aliases.get(normalized)
