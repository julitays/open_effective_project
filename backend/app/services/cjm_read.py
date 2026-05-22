from __future__ import annotations

from app.models.cjm import CommunicationPoint, ProjectBarrier
from app.models.lpr import LPRImportanceFactor, LPRProfile
from app.models.project import ClientExpectation, Project, ProjectGoal, ProjectKPI
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
            project_scale=None,
            lifecycle_stage=project.current_phase,
            project_status=project.status,
            short_description=None,
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
            influence_level=lpr.influence_level,
            activity_status=lpr.engagement_status,
            relationship_status=None,
            importance_factors=[
                self._importance_factor(factor)
                for factor in sorted(
                    lpr.importance_factors,
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
        )

    def _barrier(self, barrier: ProjectBarrier) -> CJMBarrier:
        return CJMBarrier(
            barrier_id=barrier.source_id,
            barrier_title=barrier.barrier_title,
            barrier_type=barrier.barrier_type,
            time_status=barrier.time_status,
            criticality=barrier.criticality,
            status=barrier.status,
            relevance_status=None,
            confidence_level=None,
            linked_kpi_text=barrier.linked_kpi_text,
            related_lpr_code=None,
            source_type=barrier.source_type,
            source_id=barrier.source_id,
            evidence_quote=None,
        )

    def _expectation(self, expectation: ClientExpectation) -> CJMExpectation:
        return CJMExpectation(
            expectation_id=expectation.source_id,
            expectation_text=expectation.expectation_text,
            expectation_type=expectation.expectation_type,
            explicitness=expectation.explicitness,
            criticality=expectation.criticality,
            relevance_status=None,
            confidence_level=None,
            linked_kpi_text=expectation.linked_kpi_text,
            related_lpr_code=None,
            source=None,
            evidence_quote=None,
        )

    def _kpi(self, kpi: ProjectKPI) -> CJMKPI:
        return CJMKPI(
            kpi_id=kpi.kpi_code,
            metric_name=kpi.metric_name,
            target_value=kpi.target_value,
            current_value=kpi.current_value,
            unit=kpi.unit,
            status=kpi.status,
        )

    def _communication(self, point: CommunicationPoint) -> CJMCommunicationPoint:
        return CJMCommunicationPoint(
            communication_id=point.source_id,
            channel=point.point_type,
            summary=point.summary,
            outcome=point.outcome,
            cjm_stage=point.cjm_stage,
        )

    def _goal(self, goal: ProjectGoal) -> CJMGoal:
        return CJMGoal(
            goal_id=goal.source_id,
            goal_text=goal.goal_text,
            goal_type=goal.goal_type,
            success_criteria=goal.success_criteria,
            status=goal.status,
        )
