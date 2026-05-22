from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core.db import SessionLocal
from app.models.action_plan import BarrierMitigationPlan
from app.models.cjm import CommunicationPoint, ProjectBarrier
from app.models.lpr import LPRImportanceFactor, LPRProfile
from app.models.project import ClientExpectation, Project, ProjectGoal, ProjectKPI
from app.services.imports.cjm_excel_reader import read_cjm_workbook
from app.services.imports.cjm_report import DEFAULT_REPORT_DIR, write_import_report
from app.services.imports.cjm_validator import NormalizedRow, ValidationResult, validate_cjm_workbook

ImportMode = Literal["dry-run", "commit"]


@dataclass(slots=True)
class ImportRunResult:
    mode: ImportMode
    status: str
    report_path: Path
    validation: ValidationResult
    database_counts: dict[str, dict[str, int]]

    @property
    def committed(self) -> bool:
        return self.status == "committed"


def _text(value: object) -> str:
    return "" if value is None else str(value).strip()


def _increment(counts: dict[str, dict[str, int]], entity: str, action: str) -> None:
    counts.setdefault(entity, {"created": 0, "updated": 0})
    counts[entity].setdefault(action, 0)
    counts[entity][action] += 1


def should_skip_plan_commit(row: NormalizedRow) -> bool:
    return _text(row.values.get("Статус подтверждения")) == "ai_hypothesis"


class CJMImporter:
    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session] | object = SessionLocal,
        report_dir: str | Path = DEFAULT_REPORT_DIR,
    ) -> None:
        self.session_factory = session_factory
        self.report_dir = Path(report_dir)

    def run(self, file_path: str | Path, mode: ImportMode) -> ImportRunResult:
        workbook = read_cjm_workbook(file_path)
        validation = validate_cjm_workbook(workbook, mode=mode)
        database_counts: dict[str, dict[str, int]] = {}
        status = "validated" if not validation.has_errors else "validation_failed"

        if mode == "commit" and not validation.has_errors:
            session = self.session_factory()  # type: ignore[operator]
            try:
                self._add_commit_reference_issues(session, validation)
                if validation.has_errors:
                    session.rollback()
                    status = "validation_failed"
                else:
                    database_counts = self._commit(session, validation)
                    session.commit()
                    status = "committed"
            except Exception as exc:
                session.rollback()
                validation.add_issue(
                    "error",
                    "commit",
                    None,
                    f"Commit-загрузка остановлена: {exc.__class__.__name__}: {exc}",
                )
                status = "commit_failed"
            finally:
                session.close()

        report_path = write_import_report(
            validation,
            mode=mode,
            status=status,
            database_counts=database_counts,
            report_dir=self.report_dir,
        )
        return ImportRunResult(mode, status, report_path, validation, database_counts)

    def _add_commit_reference_issues(self, session: Session, validation: ValidationResult) -> None:
        if validation.primary_project_id is None:
            return

        project = session.scalar(
            select(Project).where(Project.project_code == validation.primary_project_id)
        )
        workbook_lprs = validation.identifiers["lpr_ids"]
        workbook_barriers = validation.identifiers["barrier_ids"]

        existing_lprs: set[str] = set()
        existing_barriers: set[str] = set()
        if project is not None:
            existing_lprs = set(
                session.scalars(
                    select(LPRProfile.lpr_code).where(LPRProfile.project_id == project.id)
                ).all()
            )
            existing_barriers = set(
                session.scalars(
                    select(ProjectBarrier.source_id).where(
                        ProjectBarrier.project_id == project.id,
                        ProjectBarrier.source_type == "manual_excel",
                        ProjectBarrier.source_id.is_not(None),
                    )
                ).all()
            )

        for row in validation.normalized_sheets["03_Важности ЛПР"]:
            lpr_code = _text(row.values.get("LPR ID"))
            if lpr_code and lpr_code not in workbook_lprs and lpr_code not in existing_lprs:
                validation.add_issue(
                    "error",
                    row.sheet_name,
                    row.row_number,
                    "Для важности ЛПР не найден LPR ID ни в файле, ни в БД.",
                    "LPR ID",
                    lpr_code,
                )

        for row in validation.normalized_sheets["08_Планы действий"]:
            if should_skip_plan_commit(row):
                continue
            barrier_code = _text(row.values.get("Связанный Barrier ID"))
            if (
                barrier_code
                and barrier_code not in workbook_barriers
                and barrier_code not in existing_barriers
            ):
                validation.add_issue(
                    "error",
                    row.sheet_name,
                    row.row_number,
                    "Для плана устранения не найден Barrier ID ни в файле, ни в БД.",
                    "Связанный Barrier ID",
                    barrier_code,
                )

    def _commit(
        self,
        session: Session,
        validation: ValidationResult,
    ) -> dict[str, dict[str, int]]:
        counts: dict[str, dict[str, int]] = {}
        project = self._upsert_project(session, validation, counts)
        session.flush()
        lprs = self._upsert_lprs(session, project, validation, counts)
        session.flush()
        self._upsert_importance_factors(session, project, validation, lprs, counts)
        barriers = self._upsert_barriers(session, project, validation, counts)
        self._upsert_expectations(session, project, validation, counts)
        self._upsert_kpis(session, project, validation, counts)
        self._upsert_goals(session, project, validation, counts)
        self._upsert_communication_points(session, project, validation, counts)
        session.flush()
        self._upsert_plans(session, project, validation, barriers, counts)
        return counts

    def _upsert_project(
        self,
        session: Session,
        validation: ValidationResult,
        counts: dict[str, dict[str, int]],
    ) -> Project:
        project_code = validation.primary_project_id
        if project_code is None:
            raise ValueError("Project ID is missing from validated workbook.")

        row = validation.normalized_sheets["01_Паспорт проекта"][0]
        project = session.scalar(select(Project).where(Project.project_code == project_code))
        if project is None:
            project = Project(project_code=project_code)
            session.add(project)
            _increment(counts, "projects", "created")
        else:
            _increment(counts, "projects", "updated")

        project.project_type = _text(row.values.get("Направление проекта")) or project.project_type
        project.external_project_id = _text(row.values.get("External project ID")) or None
        project.working_project_code = _text(row.values.get("Рабочий код проекта")) or None
        project.current_phase = (
            _text(row.values.get("Этап жизненного цикла")) or project.current_phase
        )
        project.status = _text(row.values.get("Статус проекта")) or project.status
        return project

    def _upsert_lprs(
        self,
        session: Session,
        project: Project,
        validation: ValidationResult,
        counts: dict[str, dict[str, int]],
    ) -> dict[str, LPRProfile]:
        existing = {
            lpr.lpr_code: lpr
            for lpr in session.scalars(
                select(LPRProfile).where(LPRProfile.project_id == project.id)
            ).all()
        }
        lprs = dict(existing)

        for row in validation.normalized_sheets["02_ЛПР"]:
            lpr_code = _text(row.values.get("LPR ID"))
            lpr = lprs.get(lpr_code)
            if lpr is None:
                lpr = LPRProfile(
                    project_id=project.id,
                    lpr_code=lpr_code,
                    stakeholder_role=_text(row.values.get("Роль / зона влияния")),
                )
                session.add(lpr)
                lprs[lpr_code] = lpr
                _increment(counts, "lpr_profiles", "created")
            else:
                _increment(counts, "lpr_profiles", "updated")

            lpr.external_lpr_id = _text(row.values.get("External LPR ID")) or None
            lpr.stakeholder_role = _text(row.values.get("Роль / зона влияния"))
            lpr.influence_level = _text(row.values.get("Уровень влияния")) or None
            lpr.engagement_status = (
                _text(row.values.get("Статус активности"))
                or _text(row.values.get("Предполагаемое отношение к OPEN/услуге"))
                or None
            )

        return lprs

    def _upsert_importance_factors(
        self,
        session: Session,
        project: Project,
        validation: ValidationResult,
        lprs: dict[str, LPRProfile],
        counts: dict[str, dict[str, int]],
    ) -> None:
        for row in validation.normalized_sheets["03_Важности ЛПР"]:
            lpr = lprs.get(_text(row.values.get("LPR ID")))
            if lpr is None:
                lpr = session.scalar(
                    select(LPRProfile).where(
                        LPRProfile.project_id == project.id,
                        LPRProfile.lpr_code == _text(row.values.get("LPR ID")),
                    )
                )
            if lpr is None:
                continue

            factor_type = _text(row.values.get("_factor_type")) or "other"
            factor_text = _text(row.values.get("Важность"))
            factor = session.scalar(
                select(LPRImportanceFactor).where(
                    LPRImportanceFactor.project_id == project.id,
                    LPRImportanceFactor.lpr_id == lpr.id,
                    LPRImportanceFactor.factor_type == factor_type,
                    LPRImportanceFactor.factor_text == factor_text,
                )
            )
            if factor is None:
                factor = LPRImportanceFactor(
                    project_id=project.id,
                    lpr_id=lpr.id,
                    factor_type=factor_type,
                    factor_text=factor_text,
                )
                session.add(factor)
                _increment(counts, "lpr_importance_factors", "created")
            else:
                _increment(counts, "lpr_importance_factors", "updated")
            factor.importance_level = _text(row.values.get("Критичность")) or None
            factor.source_type = _text(row.values.get("Источник вывода")) or "manual_excel"

    def _upsert_barriers(
        self,
        session: Session,
        project: Project,
        validation: ValidationResult,
        counts: dict[str, dict[str, int]],
    ) -> dict[str, ProjectBarrier]:
        barriers = {
            barrier.source_id: barrier
            for barrier in session.scalars(
                select(ProjectBarrier).where(
                    ProjectBarrier.project_id == project.id,
                    ProjectBarrier.source_type == "manual_excel",
                    ProjectBarrier.source_id.is_not(None),
                )
            ).all()
        }

        for row in validation.normalized_sheets["04_Барьеры"]:
            barrier_code = _text(row.values.get("Barrier ID"))
            barrier = barriers.get(barrier_code)
            if barrier is None:
                barrier = ProjectBarrier(
                    project_id=project.id,
                    barrier_title=_text(row.values.get("Название барьера")),
                    barrier_type=_text(row.values.get("Тип барьера")),
                    time_status=_text(row.values.get("Временной статус")),
                    criticality=_text(row.values.get("Критичность")),
                    status=_text(row.values.get("Статус барьера")) or "unknown",
                    source_type="manual_excel",
                    source_id=barrier_code,
                )
                session.add(barrier)
                barriers[barrier_code] = barrier
                _increment(counts, "project_barriers", "created")
            else:
                _increment(counts, "project_barriers", "updated")
            barrier.barrier_title = _text(row.values.get("Название барьера"))
            barrier.barrier_type = _text(row.values.get("Тип барьера"))
            barrier.time_status = _text(row.values.get("Временной статус"))
            barrier.criticality = _text(row.values.get("Критичность"))
            barrier.status = _text(row.values.get("Статус барьера")) or "unknown"
        return barriers

    def _upsert_expectations(
        self,
        session: Session,
        project: Project,
        validation: ValidationResult,
        counts: dict[str, dict[str, int]],
    ) -> None:
        for row in validation.normalized_sheets["05_Ожидания клиента"]:
            expectation_text = _text(row.values.get("Ожидание клиента"))
            expectation_type = _text(row.values.get("Тип ожидания"))
            expectation = session.scalar(
                select(ClientExpectation).where(
                    ClientExpectation.project_id == project.id,
                    ClientExpectation.expectation_text == expectation_text,
                    ClientExpectation.expectation_type == expectation_type,
                )
            )
            if expectation is None:
                expectation = ClientExpectation(
                    project_id=project.id,
                    expectation_text=expectation_text,
                    expectation_type=expectation_type,
                    explicitness=_text(row.values.get("Явное или неявное")) or "unknown",
                    criticality=_text(row.values.get("Критичность")),
                )
                session.add(expectation)
                _increment(counts, "client_expectations", "created")
            else:
                _increment(counts, "client_expectations", "updated")
            expectation.explicitness = _text(row.values.get("Явное или неявное")) or "unknown"
            expectation.criticality = _text(row.values.get("Критичность"))

    def _upsert_kpis(
        self,
        session: Session,
        project: Project,
        validation: ValidationResult,
        counts: dict[str, dict[str, int]],
    ) -> None:
        for row in validation.normalized_sheets["06_KPI и критерии успеха"]:
            kpi_code = _text(row.values.get("KPI ID"))
            kpi = session.scalar(
                select(ProjectKPI).where(
                    ProjectKPI.project_id == project.id,
                    ProjectKPI.kpi_code == kpi_code,
                )
            )
            if kpi is None:
                kpi = ProjectKPI(
                    project_id=project.id,
                    kpi_code=kpi_code,
                    metric_name=_text(row.values.get("Название KPI / критерия успеха")),
                )
                session.add(kpi)
                _increment(counts, "project_kpis", "created")
            else:
                _increment(counts, "project_kpis", "updated")
            kpi.metric_name = _text(row.values.get("Название KPI / критерия успеха"))
            kpi.status = _text(row.values.get("Статус актуальности")) or "tracked"

    def _upsert_communication_points(
        self,
        session: Session,
        project: Project,
        validation: ValidationResult,
        counts: dict[str, dict[str, int]],
    ) -> None:
        for row in validation.normalized_sheets["07_Каналы взаимодействия"]:
            summary = self._communication_summary(row)
            point_type = _text(row.values.get("Канал")) or "unknown"
            point = session.scalar(
                select(CommunicationPoint).where(
                    CommunicationPoint.project_id == project.id,
                    CommunicationPoint.point_type == point_type,
                    CommunicationPoint.summary == summary,
                )
            )
            if point is None:
                point = CommunicationPoint(
                    project_id=project.id,
                    point_type=point_type,
                    summary=summary,
                )
                session.add(point)
                _increment(counts, "communication_points", "created")
            else:
                _increment(counts, "communication_points", "updated")
            point.outcome = (
                _text(row.values.get("Комментарий"))
                or _text(row.values.get("Источник"))
                or None
            )

    def _upsert_goals(
        self,
        session: Session,
        project: Project,
        validation: ValidationResult,
        counts: dict[str, dict[str, int]],
    ) -> None:
        for row in validation.normalized_sheets["08_Цели проекта"]:
            goal_text = _text(row.values.get("Цель проекта"))
            goal_type = _text(row.values.get("Тип цели"))
            goal = session.scalar(
                select(ProjectGoal).where(
                    ProjectGoal.project_id == project.id,
                    ProjectGoal.goal_text == goal_text,
                    ProjectGoal.goal_type == goal_type,
                )
            )
            if goal is None:
                goal = ProjectGoal(
                    project_id=project.id,
                    goal_text=goal_text,
                    goal_type=goal_type,
                )
                session.add(goal)
                _increment(counts, "project_goals", "created")
            else:
                _increment(counts, "project_goals", "updated")
            goal.success_criteria = (
                _text(row.values.get("Связанный KPI / критерий"))
                or _text(row.values.get("Комментарий"))
                or None
            )
            goal.status = _text(row.values.get("Статус актуальности")) or "open"

    def _communication_summary(self, row: NormalizedRow) -> str:
        details = [
            _text(row.values.get("Тема взаимодействия")),
            f"client_side={_text(row.values.get('Сторона клиента: LPR ID или роль')) or 'unknown'}",
            f"external_lpr_id={_text(row.values.get('External LPR ID')) or 'unknown'}",
            f"open_side={_text(row.values.get('Сторона OPEN: роль')) or 'unknown'}",
            f"frequency={_text(row.values.get('Частота')) or 'unknown'}",
            f"criticality={_text(row.values.get('Критичность')) or 'unknown'}",
        ]
        actuality = _text(row.values.get("Статус актуальности"))
        if actuality:
            details.append(f"actuality={actuality}")
        return " | ".join(details)

    def _upsert_plans(
        self,
        session: Session,
        project: Project,
        validation: ValidationResult,
        barriers: dict[str, ProjectBarrier],
        counts: dict[str, dict[str, int]],
    ) -> None:
        for row in validation.normalized_sheets["08_Планы действий"]:
            if should_skip_plan_commit(row):
                _increment(counts, "barrier_mitigation_plans", "skipped")
                continue
            barrier_code = _text(row.values.get("Связанный Barrier ID"))
            barrier = barriers.get(barrier_code)
            if barrier is None:
                barrier = session.scalar(
                    select(ProjectBarrier).where(
                        ProjectBarrier.project_id == project.id,
                        ProjectBarrier.source_type == "manual_excel",
                        ProjectBarrier.source_id == barrier_code,
                    )
                )
            if barrier is None:
                continue

            action_type = _text(row.values.get("Тип действия"))
            action_text = _text(row.values.get("Описание действия"))
            plan = session.scalar(
                select(BarrierMitigationPlan).where(
                    BarrierMitigationPlan.project_id == project.id,
                    BarrierMitigationPlan.barrier_id == barrier.id,
                    BarrierMitigationPlan.action_type == action_type,
                    BarrierMitigationPlan.action_text == action_text,
                )
            )
            if plan is None:
                plan = BarrierMitigationPlan(
                    project_id=project.id,
                    barrier_id=barrier.id,
                    action_type=action_type,
                    action_text=action_text,
                    owner_role=_text(row.values.get("Ответственная роль")),
                    status=_text(row.values.get("Статус")) or "unknown",
                )
                session.add(plan)
                _increment(counts, "barrier_mitigation_plans", "created")
            else:
                _increment(counts, "barrier_mitigation_plans", "updated")
            plan.owner_role = _text(row.values.get("Ответственная роль"))
            plan.due_period = _text(row.values.get("Срок / период")) or None
            plan.status = _text(row.values.get("Статус")) or "unknown"
            plan.confirmation_status = _text(row.values.get("Статус подтверждения")) or None
            plan.expected_effect = _text(row.values.get("Ожидаемый эффект")) or None
