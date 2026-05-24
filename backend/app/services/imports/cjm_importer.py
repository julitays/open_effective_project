from __future__ import annotations

import re
from dataclasses import dataclass
from math import isnan
from pathlib import Path
from typing import Literal

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.db import SessionLocal
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
    force: bool = False

    @property
    def committed(self) -> bool:
        return self.status == "committed"


def _text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and isnan(value):
        return ""
    text = str(value).strip()
    return "" if text.lower() == "nan" else text


def _first_text(row: NormalizedRow, *field_names: str) -> str:
    for field_name in field_names:
        value = _text(row.values.get(field_name))
        if value:
            return value
    return ""


def _increment(counts: dict[str, dict[str, int]], entity: str, action: str) -> None:
    counts.setdefault(entity, {"created": 0, "updated": 0})
    counts[entity].setdefault(action, 0)
    counts[entity][action] += 1


def normalize_external_lpr_aliases(*values: object) -> str | None:
    aliases: list[str] = []
    seen: set[str] = set()

    for value in values:
        for alias in re.split(r"\s*[;,\n]\s*", _text(value)):
            if not alias or alias in seen:
                continue
            aliases.append(alias)
            seen.add(alias)

    return "; ".join(aliases) or None


def _manual_update_marker(entity: object | None) -> str:
    return _text(getattr(entity, "updated_by", None))


class CJMImporter:
    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session] | object = SessionLocal,
        report_dir: str | Path = DEFAULT_REPORT_DIR,
        force: bool = False,
    ) -> None:
        self.session_factory = session_factory
        self.report_dir = Path(report_dir)
        self.force = force

    def _skip_manual_update(
        self,
        validation: ValidationResult,
        row: NormalizedRow,
        counts: dict[str, dict[str, int]],
        entity_name: str,
        entity_label: str,
        entity: object,
    ) -> bool:
        manual_marker = _manual_update_marker(entity)
        if not manual_marker:
            return False
        if self.force:
            self._clear_manual_update_marker(entity)
            return False

        _increment(counts, entity_name, "skipped_manual")
        validation.add_issue(
            "warning",
            row.sheet_name,
            row.row_number,
            (
                f"Запись '{entity_label}' была изменена вручную пользователем "
                f"'{manual_marker}'. Импорт пропустил обновление без --force."
            ),
            field_name="updated_by",
            raw_value=entity_label,
            current_mapping=manual_marker,
            issue_type="manual_update_protection",
            suggested_action=(
                "После ручных правок Supabase считается источником истины. "
                "Проверьте запись в системе или повторите commit с --force, "
                "если Excel должен перезаписать ручные изменения."
            ),
        )
        return True

    def _clear_manual_update_marker(self, entity: object) -> None:
        if hasattr(entity, "updated_by"):
            setattr(entity, "updated_by", None)

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
            force=self.force,
            report_dir=self.report_dir,
        )
        return ImportRunResult(mode, status, report_path, validation, database_counts, self.force)

    def _add_commit_reference_issues(self, session: Session, validation: ValidationResult) -> None:
        if validation.primary_project_id is None:
            return

        project = session.scalar(
            select(Project).where(Project.project_code == validation.primary_project_id)
        )
        workbook_lprs = validation.identifiers["lpr_ids"]

        existing_lprs: set[str] = set()
        if project is not None:
            existing_lprs = set(
                session.scalars(
                    select(LPRProfile.lpr_code).where(LPRProfile.project_id == project.id)
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
        external_project_id = _text(row.values.get("External project ID"))
        project_filters = [Project.project_code == project_code]
        if external_project_id:
            project_filters.append(Project.external_project_id == external_project_id)
        project = session.scalar(select(Project).where(or_(*project_filters)))
        if project is None:
            project = Project(project_code=project_code)
            session.add(project)
            _increment(counts, "projects", "created")
        else:
            if self._skip_manual_update(
                validation,
                row,
                counts,
                "projects",
                project_code,
                project,
            ):
                return project
            _increment(counts, "projects", "updated")

        project.project_type = _text(row.values.get("Направление проекта")) or project.project_type
        project.external_project_id = external_project_id or None
        project.working_project_code = _text(row.values.get("Рабочий код проекта")) or None
        project.project_scale = _text(row.values.get("Масштаб проекта")) or None
        project.known_regions = _text(row.values.get("Известные регионы")) or None
        project.primary_operational_model = (
            _text(row.values.get("Основная операционная модель")) or None
        )
        project.additional_operational_contours = (
            _text(row.values.get("Дополнительные операционные контуры")) or None
        )
        project.current_phase = (
            _text(row.values.get("Этап жизненного цикла")) or project.current_phase
        )
        project.status = _text(row.values.get("Статус проекта")) or project.status
        project.start_date = _text(row.values.get("Дата старта")) or None
        project.short_description = _text(row.values.get("Краткое описание проекта")) or None
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
                if self._skip_manual_update(
                    validation,
                    row,
                    counts,
                    "lpr_profiles",
                    lpr_code,
                    lpr,
                ):
                    continue
                _increment(counts, "lpr_profiles", "updated")

            lpr.external_lpr_id = normalize_external_lpr_aliases(
                lpr.external_lpr_id,
                row.values.get("External LPR ID"),
            )
            lpr.stakeholder_role = _text(row.values.get("Роль / зона влияния"))
            lpr.influence_level = _text(row.values.get("Уровень влияния")) or None
            lpr.activity_status = _text(row.values.get("Статус активности")) or None
            lpr.relationship_status = (
                _text(row.values.get("Предполагаемое отношение к OPEN/услуге")) or None
            )
            lpr.evidence_basis = _text(row.values.get("Основание вывода")) or None
            lpr.manual_comment = (
                _text(row.values.get("Комментарий для ручного уточнения")) or None
            )
            lpr.engagement_status = lpr.activity_status or lpr.relationship_status

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
                )
            )
            if factor is None:
                factor = session.scalar(
                    select(LPRImportanceFactor).where(
                        LPRImportanceFactor.project_id == project.id,
                        LPRImportanceFactor.lpr_id == lpr.id,
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
                if self._skip_manual_update(
                    validation,
                    row,
                    counts,
                    "lpr_importance_factors",
                    f"{lpr.lpr_code}:{factor_type}",
                    factor,
                ):
                    continue
                _increment(counts, "lpr_importance_factors", "updated")
            factor.factor_type = factor_type
            factor.factor_text = factor_text
            factor.importance_level = _text(row.values.get("Критичность")) or None
            factor.source_type = "manual_excel"
            factor.source_text = _text(row.values.get("Источник вывода")) or None
            factor.evidence_quote = (
                _text(row.values.get("Доказательство / короткая цитата")) or None
            )
            factor.period_or_source = _text(row.values.get("Период / источник")) or None
            factor.confidence_level = _text(row.values.get("Уверенность вывода")) or None

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
                if self._skip_manual_update(
                    validation,
                    row,
                    counts,
                    "project_barriers",
                    barrier_code,
                    barrier,
                ):
                    continue
                _increment(counts, "project_barriers", "updated")
            barrier.barrier_title = _text(row.values.get("Название барьера"))
            barrier.barrier_type = _text(row.values.get("Тип барьера"))
            barrier.time_status = _text(row.values.get("Временной статус"))
            barrier.criticality = _text(row.values.get("Критичность"))
            barrier.status = _text(row.values.get("Статус барьера")) or "unknown"
            barrier.description = _text(row.values.get("Описание барьера")) or None
            barrier.related_lpr_code = _text(row.values.get("Связанный LPR ID")) or None
            barrier.external_lpr_id = _text(row.values.get("External LPR ID")) or None
            barrier.related_importance_text = (
                _text(row.values.get("Связанная важность ЛПР")) or None
            )
            barrier.linked_kpi_text = _text(row.values.get("Связанный KPI")) or None
            barrier.source_text = _text(row.values.get("Источник")) or None
            barrier.evidence_quote = (
                _text(row.values.get("Доказательство / короткая цитата")) or None
            )
            barrier.first_seen_period = (
                _text(row.values.get("Период первого появления")) or None
            )
            barrier.last_seen_period = (
                _text(row.values.get("Период последнего появления")) or None
            )
            barrier.relevance_status = _text(row.values.get("Статус актуальности")) or None
            barrier.confidence_level = _text(row.values.get("Уверенность вывода")) or None
        return barriers

    def _upsert_expectations(
        self,
        session: Session,
        project: Project,
        validation: ValidationResult,
        counts: dict[str, dict[str, int]],
    ) -> None:
        for row in validation.normalized_sheets["05_Ожидания клиента"]:
            source_id = _text(row.values.get("Expectation ID"))
            expectation_text = _text(row.values.get("Ожидание клиента"))
            expectation_type = _text(row.values.get("Тип ожидания"))
            expectation = None
            if source_id:
                expectation = session.scalar(
                    select(ClientExpectation).where(
                        ClientExpectation.project_id == project.id,
                        ClientExpectation.source_id == source_id,
                    )
                )
            if expectation is None:
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
                    source_id=source_id or None,
                    expectation_text=expectation_text,
                    expectation_type=expectation_type,
                    explicitness=_text(row.values.get("Явное или неявное")) or "unknown",
                    criticality=_text(row.values.get("Критичность")),
                )
                session.add(expectation)
                _increment(counts, "client_expectations", "created")
            else:
                if self._skip_manual_update(
                    validation,
                    row,
                    counts,
                    "client_expectations",
                    source_id or expectation_text,
                    expectation,
                ):
                    continue
                _increment(counts, "client_expectations", "updated")
            expectation.source_id = source_id or None
            expectation.expectation_text = expectation_text
            expectation.expectation_type = expectation_type
            expectation.explicitness = _text(row.values.get("Явное или неявное")) or "unknown"
            expectation.criticality = _text(row.values.get("Критичность"))
            expectation.related_lpr_code = _text(row.values.get("Связанный LPR ID")) or None
            expectation.external_lpr_id = _text(row.values.get("External LPR ID")) or None
            expectation.related_importance_text = (
                _text(row.values.get("Связанная важность ЛПР")) or None
            )
            expectation.linked_kpi_text = _text(row.values.get("Связанный KPI")) or None
            expectation.source_text = _text(row.values.get("Источник")) or None
            expectation.evidence_quote = (
                _text(row.values.get("Доказательство / короткая цитата")) or None
            )
            expectation.relevance_status = (
                _text(row.values.get("Статус актуальности")) or None
            )
            expectation.confidence_level = _text(row.values.get("Уверенность вывода")) or None

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
                if self._skip_manual_update(
                    validation,
                    row,
                    counts,
                    "project_kpis",
                    kpi_code,
                    kpi,
                ):
                    continue
                _increment(counts, "project_kpis", "updated")
            kpi.metric_name = _text(row.values.get("Название KPI / критерия успеха"))
            kpi.kpi_type = _text(row.values.get("Тип KPI")) or None
            kpi.source_text = _text(row.values.get("Источник")) or None
            kpi.relevance_status = _text(row.values.get("Статус актуальности")) or None
            kpi.related_expectation_text = (
                _text(row.values.get("Связанное ожидание клиента")) or None
            )
            kpi.related_barrier_text = _text(row.values.get("Связанный барьер")) or None
            kpi.client_criticality = _text(row.values.get("Критичность для клиента")) or None
            kpi.comment = _text(row.values.get("Комментарий")) or None
            kpi.requires_confirmation = (
                _text(row.values.get("Требует подтверждения")) or None
            )
            kpi.status = _text(row.values.get("Статус актуальности")) or "tracked"

    def _upsert_communication_points(
        self,
        session: Session,
        project: Project,
        validation: ValidationResult,
        counts: dict[str, dict[str, int]],
    ) -> None:
        for row in validation.normalized_sheets["07_Каналы взаимодействия"]:
            source_id = _text(row.values.get("Communication ID"))
            summary = self._communication_summary(row)
            point_type = _text(row.values.get("Канал")) or "unknown"
            point = None
            if source_id:
                point = session.scalar(
                    select(CommunicationPoint).where(
                        CommunicationPoint.project_id == project.id,
                        CommunicationPoint.source_id == source_id,
                    )
                )
            if point is None:
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
                    source_id=source_id or None,
                    point_type=point_type,
                    summary=summary,
                )
                session.add(point)
                _increment(counts, "communication_points", "created")
            else:
                if self._skip_manual_update(
                    validation,
                    row,
                    counts,
                    "communication_points",
                    source_id or summary,
                    point,
                ):
                    continue
                _increment(counts, "communication_points", "updated")
            point.source_id = source_id or None
            point.point_type = point_type
            point.client_side = (
                _text(row.values.get("Сторона клиента: LPR ID или роль")) or None
            )
            point.external_lpr_id = _text(row.values.get("External LPR ID")) or None
            point.open_side_role = _text(row.values.get("Сторона OPEN: роль")) or None
            point.topic_text = _text(row.values.get("Тема взаимодействия")) or None
            point.channel_text = _text(row.values.get("_channel_text")) or None
            point.frequency = _text(row.values.get("_frequency_text")) or None
            point.criticality = _text(row.values.get("Критичность")) or None
            point.source_text = _text(row.values.get("Источник")) or None
            point.relevance_status = _text(row.values.get("Статус актуальности")) or None
            point.comment = _text(row.values.get("Комментарий")) or None
            point.summary = summary
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
            source_id = _text(row.values.get("Goal ID"))
            goal_text = _text(row.values.get("Цель проекта"))
            goal_type = _text(row.values.get("Тип цели"))
            goal = None
            if source_id:
                goal = session.scalar(
                    select(ProjectGoal).where(
                        ProjectGoal.project_id == project.id,
                        ProjectGoal.source_id == source_id,
                    )
                )
            if goal is None:
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
                    source_id=source_id or None,
                    goal_text=goal_text,
                    goal_type=goal_type,
                )
                session.add(goal)
                _increment(counts, "project_goals", "created")
            else:
                if self._skip_manual_update(
                    validation,
                    row,
                    counts,
                    "project_goals",
                    source_id or goal_text,
                    goal,
                ):
                    continue
                _increment(counts, "project_goals", "updated")
            goal.source_id = source_id or None
            goal.goal_owner = _text(row.values.get("Владелец цели")) or None
            goal.goal_text = goal_text
            goal.goal_type = goal_type
            goal.priority = _text(row.values.get("Приоритет")) or None
            goal.related_kpi_or_criterion_text = (
                _first_text(row, "Связанный KPI / критерий", "Связанный KPI") or None
            )
            goal.success_criteria = goal.related_kpi_or_criterion_text
            goal.source_text = _text(row.values.get("Источник")) or None
            goal.relevance_status = _text(row.values.get("Статус актуальности")) or None
            goal.comment = _text(row.values.get("Комментарий")) or None
            goal.status = _text(row.values.get("Статус актуальности")) or "open"

    def _communication_summary(self, row: NormalizedRow) -> str:
        details = [
            _text(row.values.get("Тема взаимодействия")),
            f"client_side={_text(row.values.get('Сторона клиента: LPR ID или роль')) or 'unknown'}",
            f"external_lpr_id={_text(row.values.get('External LPR ID')) or 'unknown'}",
            f"open_side={_text(row.values.get('Сторона OPEN: роль')) or 'unknown'}",
            f"frequency={_text(row.values.get('_frequency_text')) or _text(row.values.get('Частота')) or 'unknown'}",
            f"criticality={_text(row.values.get('Критичность')) or 'unknown'}",
        ]
        actuality = _text(row.values.get("Статус актуальности"))
        if actuality:
            details.append(f"actuality={actuality}")
        return " | ".join(details)
