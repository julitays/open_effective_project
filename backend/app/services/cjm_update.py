from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pydantic import BaseModel

from app.models.cjm import CommunicationPoint, ProjectBarrier
from app.models.lpr import LPRProfile
from app.models.project import ClientExpectation, Project, ProjectGoal, ProjectKPI
from app.repositories.cjm_update import CJMUpdateRepository
from app.schemas.cjm import (
    CJMBarrier,
    CJMBarrierPatch,
    CJMCommunicationPoint,
    CJMCommunicationPointPatch,
    CJMExpectation,
    CJMExpectationPatch,
    CJMGoal,
    CJMGoalPatch,
    CJMKPI,
    CJMKPIPatch,
    CJMLPR,
    CJMLPRPatch,
)
from app.schemas.project import CJMProjectPassport, CJMProjectPatch
from app.services.cjm_read import CJMReadService
from app.services.imports import cjm_mappings


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

    def update_project(
        self,
        project_code: str,
        patch: CJMProjectPatch,
        updated_by: str,
    ) -> CJMProjectPassport | None:
        project = self.repository.get_project(project_code)
        if project is None:
            return None

        self._apply_patch(
            project,
            patch,
            field_map={
                "lifecycle_stage": "current_phase",
                "project_status": "status",
            },
            mappers={
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
            mappers={"relevance_status": map_relevance_status},
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
        self._mark_manual_update(point, updated_by)
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


def _map_alias(value: object, aliases: dict[str, str]) -> str | None:
    normalized = cjm_mappings.normalize_label(value)
    if not normalized:
        return None
    return aliases.get(normalized)
