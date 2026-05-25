from __future__ import annotations

from app.models.cjm import CommunicationPoint, ProjectBarrier
from app.models.lpr import LPRImportanceFactor, LPRProfile
from app.models.project import ClientExpectation, Project, ProjectContextBlock, ProjectGoal, ProjectKPI
from app.repositories.cjm_read import CJMReadRepository
from app.schemas.cjm import (
    CJMBarrier,
    CJMCommunicationPoint,
    CJMExpectation,
    CJMGoal,
    CJMKPI,
    CJMLPR,
    CJMLPRImportanceFactor,
    CJMProjectRead,
    ProjectContextBlockRead,
    ProjectEffectivenessRead,
)
from app.schemas.project import CJMProjectPassport


class CJMReadService:
    def __init__(self, repository: CJMReadRepository) -> None:
        self.repository = repository

    def list_projects(self) -> list[CJMProjectPassport]:
        return [self._project_passport(project) for project in self.repository.list_projects()]

    def get_project(self, project_code: str) -> CJMProjectPassport | None:
        project = self.repository.get_project_by_code(project_code)
        return self._project_passport(project) if project is not None else None

    def get_project_cjm(self, project_code: str) -> CJMProjectRead | None:
        project = self.repository.get_project_by_code(project_code)
        if project is None:
            return None

        return CJMProjectRead(
            project=self._project_passport(project),
            goals=self._goals(project),
            lprs=self._lprs(project),
            barriers=self._barriers(project),
            expectations=self._expectations(project),
            kpis=self._kpis(project),
            communications=self._communications(project),
        )

    def get_project_effectiveness(self, project_code: str) -> ProjectEffectivenessRead | None:
        cjm = self.get_project_cjm(project_code)
        project = self.repository.get_project_by_code(project_code)
        if cjm is None or project is None:
            return None

        stored_blocks = [
            self._context_block(block)
            for block in self.repository.list_context_blocks(project.id)
        ]
        return ProjectEffectivenessRead(
            cjm=cjm,
            context_blocks=stored_blocks or self._default_context_blocks(cjm),
        )

    def get_project_lprs(self, project_code: str) -> list[CJMLPR] | None:
        project = self.repository.get_project_by_code(project_code)
        return self._lprs(project) if project is not None else None

    def get_project_barriers(self, project_code: str) -> list[CJMBarrier] | None:
        project = self.repository.get_project_by_code(project_code)
        return self._barriers(project) if project is not None else None

    def get_project_expectations(self, project_code: str) -> list[CJMExpectation] | None:
        project = self.repository.get_project_by_code(project_code)
        return self._expectations(project) if project is not None else None

    def get_project_kpis(self, project_code: str) -> list[CJMKPI] | None:
        project = self.repository.get_project_by_code(project_code)
        return self._kpis(project) if project is not None else None

    def get_project_communications(
        self,
        project_code: str,
    ) -> list[CJMCommunicationPoint] | None:
        project = self.repository.get_project_by_code(project_code)
        return self._communications(project) if project is not None else None

    def get_project_goals(self, project_code: str) -> list[CJMGoal] | None:
        project = self.repository.get_project_by_code(project_code)
        return self._goals(project) if project is not None else None

    def _project_passport(self, project: Project) -> CJMProjectPassport:
        return CJMProjectPassport(
            project_code=project.project_code,
            external_project_id=project.external_project_id,
            working_project_code=project.working_project_code,
            direction=project.project_type,
            project_scale=project.project_scale,
            known_regions=project.known_regions,
            primary_operational_model=project.primary_operational_model,
            additional_operational_contours=project.additional_operational_contours,
            lifecycle_stage=project.current_phase,
            project_status=project.status,
            start_date=project.start_date,
            short_description=project.short_description,
        )

    def _lprs(self, project: Project) -> list[CJMLPR]:
        return [self._lpr(lpr) for lpr in self.repository.list_lprs(project.id)]

    def _barriers(self, project: Project) -> list[CJMBarrier]:
        return [self._barrier(barrier) for barrier in self.repository.list_barriers(project.id)]

    def _expectations(self, project: Project) -> list[CJMExpectation]:
        return [
            self._expectation(expectation)
            for expectation in self.repository.list_expectations(project.id)
        ]

    def _kpis(self, project: Project) -> list[CJMKPI]:
        return [self._kpi(kpi) for kpi in self.repository.list_kpis(project.id)]

    def _communications(self, project: Project) -> list[CJMCommunicationPoint]:
        return [
            self._communication(point)
            for point in self.repository.list_communications(project.id)
        ]

    def _goals(self, project: Project) -> list[CJMGoal]:
        return [self._goal(goal) for goal in self.repository.list_goals(project.id)]

    def _lpr(self, lpr: LPRProfile) -> CJMLPR:
        return CJMLPR(
            lpr_code=lpr.lpr_code,
            external_lpr_id=lpr.external_lpr_id,
            role=lpr.stakeholder_role,
            role_zone=lpr.stakeholder_role,
            influence_level=lpr.influence_level,
            activity_status=lpr.activity_status or lpr.engagement_status,
            relationship_status=lpr.relationship_status,
            evidence_basis=lpr.evidence_basis,
            manual_comment=lpr.manual_comment,
            importance_factors=[
                self._importance_factor(factor)
                for factor in sorted(
                    [
                        factor
                        for factor in lpr.importance_factors
                        if factor.archived_at is None
                    ],
                    key=lambda factor: (factor.factor_type, factor.factor_text),
                )
            ],
        )

    def _importance_factor(self, factor: LPRImportanceFactor) -> CJMLPRImportanceFactor:
        return CJMLPRImportanceFactor(
            factor_type=factor.factor_type,
            factor_text=factor.factor_text,
            criticality=factor.importance_level,
            source_type=factor.source_type,
            source_text=factor.source_text,
            evidence_quote=factor.evidence_quote,
            period_or_source=factor.period_or_source,
            confidence_level=factor.confidence_level,
        )

    def _context_block(self, block: ProjectContextBlock) -> ProjectContextBlockRead:
        return ProjectContextBlockRead(
            section_key=block.section_key,
            block_code=block.block_code,
            block_type=block.block_type,
            title=block.title,
            content=block.content,
            display_order=block.display_order,
        )

    def _default_context_blocks(self, cjm: CJMProjectRead) -> list[ProjectContextBlockRead]:
        high_barriers = [
            barrier.barrier_title
            for barrier in cjm.barriers
            if barrier.criticality == "high"
        ][:4]
        current_risks = [
            barrier.barrier_title
            for barrier in cjm.barriers
            if barrier.time_status in {"current", "repeated"}
        ][:4]
        key_expectations = [
            expectation.expectation_text
            for expectation in cjm.expectations
            if expectation.criticality in {"high", "medium"}
        ][:5]
        key_kpis = [kpi.kpi_name for kpi in cjm.kpis[:6]]

        return [
            ProjectContextBlockRead(
                section_key="summary",
                block_code="summary_001",
                block_type="management_summary",
                title="Главные выводы по CJM",
                display_order=10,
                content={
                    "critical_to_client": key_expectations
                    or ["Зафиксировать ключевые ожидания клиента через интерфейс."],
                    "main_risks": current_risks
                    or ["Добавить текущие и повторяющиеся барьеры проекта."],
                    "note": "Сводка собрана из текущих целей, ожиданий, KPI и барьеров проекта.",
                },
            ),
            ProjectContextBlockRead(
                section_key="swot",
                block_code="swot_001",
                block_type="swot",
                title="SWOT-анализ проекта",
                display_order=20,
                content={
                    "strengths": [
                        "Накопленная история проекта и восстановленный CJM-контекст.",
                        "Есть связка целей, KPI, ожиданий и барьеров.",
                    ],
                    "weaknesses": high_barriers
                    or ["Часть проектного контекста требует ручного уточнения."],
                    "opportunities": [
                        "Перевести управление проектом из файлов в единый web-контур.",
                        "Связать цели клиента с KPI и регулярной коммуникацией.",
                    ],
                    "threats": current_risks
                    or ["Риски пока нужно детализировать через карту барьеров."],
                },
            ),
            ProjectContextBlockRead(
                section_key="risk_map",
                block_code="risk_map_001",
                block_type="risk_list",
                title="Карта рисков",
                display_order=30,
                content={
                    "items": [
                        {
                            "title": barrier.barrier_title,
                            "level": barrier.criticality,
                            "status": barrier.status,
                            "description": barrier.description,
                            "linked_kpi_text": barrier.linked_kpi_text,
                        }
                        for barrier in cjm.barriers
                    ],
                },
            ),
            ProjectContextBlockRead(
                section_key="effectiveness_layers",
                block_code="effectiveness_layers_001",
                block_type="product_layers",
                title="Слои эффективности",
                display_order=40,
                content={
                    "layers": [
                        {"title": "Люди", "status": f"{len(cjm.lprs)} ЛПР / ролей влияния"},
                        {"title": "Клиентские ожидания", "status": f"{len(cjm.expectations)} ожиданий"},
                        {"title": "Операционные барьеры", "status": f"{len(cjm.barriers)} барьеров"},
                        {"title": "KPI проекта", "status": f"{len(cjm.kpis)} KPI / критериев"},
                    ],
                },
            ),
            ProjectContextBlockRead(
                section_key="interpretation_rules",
                block_code="interpretation_rules_001",
                block_type="rules",
                title="Правила интерпретации",
                display_order=50,
                content={
                    "rules": [
                        "Не смешивать фактический KPI и восприятие клиента: оба слоя важны.",
                        "Ожидания ЛПР читать через роль и уровень влияния.",
                        "Барьеры со статусом repeated держать отдельно от разовых отклонений.",
                    ],
                },
            ),
            ProjectContextBlockRead(
                section_key="kpi_context",
                block_code="kpi_context_001",
                block_type="kpi_summary",
                title="KPI проекта",
                display_order=60,
                content={"items": key_kpis},
            ),
        ]

    def _barrier(self, barrier: ProjectBarrier) -> CJMBarrier:
        return CJMBarrier(
            barrier_id=barrier.source_id,
            barrier_code=barrier.source_id,
            barrier_title=barrier.barrier_title,
            barrier_type=barrier.barrier_type,
            time_status=barrier.time_status,
            criticality=barrier.criticality,
            status=barrier.status,
            description=barrier.description,
            relevance_status=barrier.relevance_status,
            confidence_level=barrier.confidence_level,
            linked_kpi_text=barrier.linked_kpi_text,
            related_lpr_code=barrier.related_lpr_code,
            external_lpr_id=barrier.external_lpr_id,
            related_importance_text=barrier.related_importance_text,
            source_type=barrier.source_type,
            source_id=barrier.source_id,
            source_text=barrier.source_text,
            evidence_quote=barrier.evidence_quote,
            first_seen_period=barrier.first_seen_period,
            last_seen_period=barrier.last_seen_period,
        )

    def _expectation(self, expectation: ClientExpectation) -> CJMExpectation:
        return CJMExpectation(
            expectation_id=expectation.source_id,
            expectation_code=expectation.source_id,
            expectation_text=expectation.expectation_text,
            expectation_type=expectation.expectation_type,
            explicitness=expectation.explicitness,
            criticality=expectation.criticality,
            relevance_status=expectation.relevance_status,
            confidence_level=expectation.confidence_level,
            linked_kpi_text=expectation.linked_kpi_text,
            related_lpr_code=expectation.related_lpr_code,
            external_lpr_id=expectation.external_lpr_id,
            related_importance_text=expectation.related_importance_text,
            source=expectation.source_text,
            source_text=expectation.source_text,
            evidence_quote=expectation.evidence_quote,
        )

    def _kpi(self, kpi: ProjectKPI) -> CJMKPI:
        return CJMKPI(
            kpi_id=kpi.kpi_code,
            kpi_code=kpi.kpi_code,
            kpi_name=kpi.metric_name,
            metric_name=kpi.metric_name,
            kpi_type=kpi.kpi_type,
            source_text=kpi.source_text,
            relevance_status=kpi.relevance_status,
            related_expectation_text=kpi.related_expectation_text,
            related_barrier_text=kpi.related_barrier_text,
            client_criticality=kpi.client_criticality,
            comment=kpi.comment,
            requires_confirmation=kpi.requires_confirmation,
            target_value=kpi.target_value,
            current_value=kpi.current_value,
            unit=kpi.unit,
            status=kpi.status,
        )

    def _communication(self, point: CommunicationPoint) -> CJMCommunicationPoint:
        return CJMCommunicationPoint(
            communication_id=point.source_id,
            communication_code=point.source_id,
            client_side=point.client_side,
            external_lpr_id=point.external_lpr_id,
            open_side_role=point.open_side_role,
            topic_type=point.topic_type,
            topic_text=point.topic_text,
            channel=point.point_type,
            channel_type=point.point_type,
            channel_text=point.channel_text,
            frequency=point.frequency,
            criticality=point.criticality,
            source_text=point.source_text,
            relevance_status=point.relevance_status,
            comment=point.comment,
            summary=point.summary,
            outcome=point.outcome,
            cjm_stage=point.cjm_stage,
        )

    def _goal(self, goal: ProjectGoal) -> CJMGoal:
        return CJMGoal(
            goal_id=goal.source_id,
            goal_code=goal.source_id,
            goal_owner=goal.goal_owner,
            goal_text=goal.goal_text,
            goal_type=goal.goal_type,
            priority=goal.priority,
            related_kpi_or_criterion_text=goal.related_kpi_or_criterion_text,
            source_text=goal.source_text,
            relevance_status=goal.relevance_status,
            comment=goal.comment,
            success_criteria=goal.success_criteria,
            status=goal.status,
        )
