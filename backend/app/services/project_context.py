from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_context import (
    ProjectClientVisionItem,
    ProjectCompetitor,
    ProjectHistoryEvent,
    ProjectInterpretationRule,
    ProjectNeedPyramidItem,
    ProjectPassportFact,
    ProjectRiskItem,
    ProjectStructureMember,
    ProjectSummaryItem,
    ProjectSummaryState,
    ProjectSwotItem,
    ProjectWorkContour,
)
from app.schemas.cjm import ProjectContextBlockRead
from app.services.project_context_templates import PROJECT_CONTEXT_TEMPLATES


class ProjectContextService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def ensure_seeded(self, project: Project) -> None:
        template = self._template_for_project(project)
        if not template:
            return

        changed = False
        changed |= self._seed_passport_section(project, "header", template.get("passport_header"))
        changed |= self._seed_passport_section(project, "overview", template.get("passport_overview"))
        changed |= self._seed_passport_section(project, "service", template.get("passport_service"))
        changed |= self._seed_client_vision(project, template.get("client_vision"))
        changed |= self._seed_work_contours(project, template.get("work_contours"))
        changed |= self._seed_history(project, template.get("project_history"))
        changed |= self._seed_need_pyramid(project, "client", template.get("client_needs"))
        changed |= self._seed_need_pyramid(project, "open", template.get("open_needs"))
        changed |= self._seed_structure(project, "open", template.get("open_structure"))
        changed |= self._seed_structure(project, "client", template.get("client_structure"))
        changed |= self._seed_competitors(project, "open", template.get("competitors_open"))
        changed |= self._seed_competitors(project, "client", template.get("competitors_client"))
        changed |= self._seed_swot(project, template.get("swot"))
        changed |= self._seed_interpretation_rules(project, template.get("interpretation_rules"))
        changed |= self._seed_risk_map(project, template.get("risk_map"))
        changed |= self._seed_summary(project, template.get("summary"))

        if changed:
            self.session.commit()

    def list_blocks(self, project: Project) -> list[ProjectContextBlockRead]:
        blocks = [
            self._passport_block(project, "header", "passport_header", "passport_header_001", "facts", "Шапка проекта"),
            self._passport_block(project, "overview", "passport_overview", "passport_overview_001", "facts", "Основные параметры"),
            self._passport_block(project, "service", "passport_service", "passport_service_001", "facts", "Модель сервиса"),
            self._client_vision_block(project),
            self._work_contours_block(project),
            self._project_history_block(project),
            self._need_pyramid_block(project, "client", "client_needs", "client_needs_001", "Пирамида клиента"),
            self._need_pyramid_block(project, "open", "open_needs", "open_needs_001", "Пирамида OPEN"),
            self._structure_block(project, "open", "open_structure", "open_structure_001", "Структура OPEN"),
            self._structure_block(project, "client", "client_structure", "client_structure_001", "Структура клиента"),
            self._competitors_block(project, "open", "competitors_open", "competitors_open_001", "Конкуренты OPEN"),
            self._competitors_block(project, "client", "competitors_client", "competitors_client_001", "Конкуренты клиента"),
            self._swot_block(project),
            self._interpretation_rules_block(project),
            self._risk_map_block(project),
            self._summary_block(project),
        ]
        return [block for block in blocks if block is not None]

    def save_block(
        self,
        project: Project,
        *,
        section_key: str,
        block_code: str,
        block_type: str | None,
        title: str | None,
        content: dict[str, object],
        display_order: int,
        updated_by: str,
    ) -> ProjectContextBlockRead:
        handlers = {
            "passport_header": lambda: self._replace_passport_facts(project, "header", self._record_items(content), updated_by),
            "passport_overview": lambda: self._replace_passport_facts(project, "overview", self._record_items(content), updated_by),
            "passport_service": lambda: self._replace_passport_facts(project, "service", self._record_items(content), updated_by),
            "client_vision": lambda: self._replace_client_vision(project, self._record_items(content), updated_by),
            "work_contours": lambda: self._replace_work_contours(project, self._record_items(content), updated_by),
            "project_history": lambda: self._replace_history(project, self._record_items(content), updated_by),
            "client_needs": lambda: self._replace_need_pyramid(project, "client", self._record_items(content), updated_by),
            "open_needs": lambda: self._replace_need_pyramid(project, "open", self._record_items(content), updated_by),
            "open_structure": lambda: self._replace_structure(project, "open", self._record_items(content), updated_by),
            "client_structure": lambda: self._replace_structure(project, "client", self._record_items(content), updated_by),
            "competitors_open": lambda: self._replace_competitors(project, "open", self._record_items(content), updated_by),
            "competitors_client": lambda: self._replace_competitors(project, "client", self._record_items(content), updated_by),
            "swot": lambda: self._replace_swot(project, content, updated_by),
            "interpretation_rules": lambda: self._replace_interpretation_rules(project, content, updated_by),
            "risk_map": lambda: self._replace_risk_map(project, self._record_items(content), updated_by),
            "summary": lambda: self._replace_summary(project, title, content, updated_by),
        }
        handler = handlers.get(section_key)
        if handler is None:
            raise ValueError(f"Unsupported project context section '{section_key}'")

        handler()
        self.session.commit()

        block = self.get_block(project, section_key, block_code)
        if block is None:
            raise ValueError(f"Section '{section_key}' did not produce a readable block")

        if block_type is not None:
            block.block_type = block_type
        if title is not None:
            block.title = title
        block.display_order = display_order
        return block

    def get_block(
        self,
        project: Project,
        section_key: str,
        block_code: str,
    ) -> ProjectContextBlockRead | None:
        for block in self.list_blocks(project):
            if block.section_key == section_key and block.block_code == block_code:
                return block
        return None

    def _template_for_project(self, project: Project) -> dict[str, object] | None:
        keys = [
            project.external_project_id,
            project.working_project_code,
            project.project_code,
        ]
        for key in keys:
            if key and key in PROJECT_CONTEXT_TEMPLATES:
                return PROJECT_CONTEXT_TEMPLATES[key]
        return None

    def _seed_passport_section(self, project: Project, section_key: str, items: object) -> bool:
        exists = any(item.section_key == section_key for item in project.passport_facts if item.archived_at is None)
        if exists or not isinstance(items, list):
            return False
        self._replace_passport_facts(project, section_key, items, "system_seed")
        return True

    def _seed_client_vision(self, project: Project, items: object) -> bool:
        if any(item.archived_at is None for item in project.client_vision_items) or not isinstance(items, list):
            return False
        self._replace_client_vision(project, items, "system_seed")
        return True

    def _seed_work_contours(self, project: Project, items: object) -> bool:
        if any(item.archived_at is None for item in project.work_contours) or not isinstance(items, list):
            return False
        self._replace_work_contours(project, items, "system_seed")
        return True

    def _seed_history(self, project: Project, items: object) -> bool:
        if any(item.archived_at is None for item in project.history_events) or not isinstance(items, list):
            return False
        self._replace_history(project, items, "system_seed")
        return True

    def _seed_need_pyramid(self, project: Project, side: str, items: object) -> bool:
        exists = any(item.side == side for item in project.need_pyramid_items if item.archived_at is None)
        if exists or not isinstance(items, list):
            return False
        self._replace_need_pyramid(project, side, items, "system_seed")
        return True

    def _seed_structure(self, project: Project, side: str, items: object) -> bool:
        exists = any(item.side == side for item in project.structure_members if item.archived_at is None)
        if exists or not isinstance(items, list):
            return False
        self._replace_structure(project, side, items, "system_seed")
        return True

    def _seed_competitors(self, project: Project, side: str, items: object) -> bool:
        exists = any(item.side == side for item in project.competitors if item.archived_at is None)
        if exists or not isinstance(items, list):
            return False
        self._replace_competitors(project, side, items, "system_seed")
        return True

    def _seed_swot(self, project: Project, value: object) -> bool:
        if any(item.archived_at is None for item in project.swot_items) or not isinstance(value, dict):
            return False
        self._replace_swot(project, value, "system_seed")
        return True

    def _seed_interpretation_rules(self, project: Project, items: object) -> bool:
        if any(item.archived_at is None for item in project.interpretation_rules) or not isinstance(items, list):
            return False
        self._replace_interpretation_rules(project, {"rules": items}, "system_seed")
        return True

    def _seed_risk_map(self, project: Project, items: object) -> bool:
        if any(item.archived_at is None for item in project.risk_items) or not isinstance(items, list):
            return False
        self._replace_risk_map(project, items, "system_seed")
        return True

    def _seed_summary(self, project: Project, value: object) -> bool:
        has_items = any(item.archived_at is None for item in project.summary_items)
        has_state = project.summary_state is not None and project.summary_state.archived_at is None
        if has_items or has_state or not isinstance(value, dict):
            return False
        self._replace_summary(project, value.get("title"), value, "system_seed")
        return True

    def _replace_passport_facts(
        self,
        project: Project,
        section_key: str,
        items: list[dict[str, object]],
        updated_by: str,
    ) -> None:
        self._archive_rows(
            select(ProjectPassportFact).where(
                ProjectPassportFact.project_id == project.id,
                ProjectPassportFact.section_key == section_key,
                ProjectPassportFact.archived_at.is_(None),
            ),
            updated_by,
        )
        for index, item in enumerate(items):
            label = self._text(item.get("label"))
            value = self._text(item.get("value"))
            if not label or not value:
                continue
            self.session.add(
                ProjectPassportFact(
                    project_id=project.id,
                    section_key=section_key,
                    label=label,
                    value=value,
                    display_order=index,
                    updated_by=updated_by,
                )
            )

    def _replace_client_vision(
        self,
        project: Project,
        items: list[dict[str, object]],
        updated_by: str,
    ) -> None:
        self._archive_rows(
            select(ProjectClientVisionItem).where(
                ProjectClientVisionItem.project_id == project.id,
                ProjectClientVisionItem.archived_at.is_(None),
            ),
            updated_by,
        )
        for index, item in enumerate(items):
            title = self._text(item.get("title"))
            value = self._text(item.get("value"))
            if not title or not value:
                continue
            self.session.add(
                ProjectClientVisionItem(
                    project_id=project.id,
                    title=title,
                    value_text=value,
                    use_text=self._text(item.get("use")),
                    display_order=index,
                    updated_by=updated_by,
                )
            )

    def _replace_work_contours(
        self,
        project: Project,
        items: list[dict[str, object]],
        updated_by: str,
    ) -> None:
        self._archive_rows(
            select(ProjectWorkContour).where(
                ProjectWorkContour.project_id == project.id,
                ProjectWorkContour.archived_at.is_(None),
            ),
            updated_by,
        )
        for index, item in enumerate(items):
            contour = self._text(item.get("contour"))
            text = self._text(item.get("text"))
            if not contour or not text:
                continue
            self.session.add(
                ProjectWorkContour(
                    project_id=project.id,
                    contour_name=contour,
                    owner_role=self._text(item.get("owner")),
                    description=text,
                    display_order=index,
                    updated_by=updated_by,
                )
            )

    def _replace_history(
        self,
        project: Project,
        items: list[dict[str, object]],
        updated_by: str,
    ) -> None:
        self._archive_rows(
            select(ProjectHistoryEvent).where(
                ProjectHistoryEvent.project_id == project.id,
                ProjectHistoryEvent.archived_at.is_(None),
            ),
            updated_by,
        )
        for index, item in enumerate(items):
            year = self._text(item.get("year"))
            title = self._text(item.get("title"))
            if not year or not title:
                continue
            self.session.add(
                ProjectHistoryEvent(
                    project_id=project.id,
                    year_label=year,
                    event_title=title,
                    description=self._text(item.get("text")),
                    display_order=index,
                    updated_by=updated_by,
                )
            )

    def _replace_need_pyramid(
        self,
        project: Project,
        side: str,
        items: list[dict[str, object]],
        updated_by: str,
    ) -> None:
        self._archive_rows(
            select(ProjectNeedPyramidItem).where(
                ProjectNeedPyramidItem.project_id == project.id,
                ProjectNeedPyramidItem.side == side,
                ProjectNeedPyramidItem.archived_at.is_(None),
            ),
            updated_by,
        )
        for index, item in enumerate(items):
            level = self._text(item.get("level"))
            title = self._text(item.get("title"))
            if not level or not title:
                continue
            self.session.add(
                ProjectNeedPyramidItem(
                    project_id=project.id,
                    side=side,
                    level_label=level,
                    title=title,
                    description=self._text(item.get("description")),
                    display_order=index,
                    updated_by=updated_by,
                )
            )

    def _replace_structure(
        self,
        project: Project,
        side: str,
        items: list[dict[str, object]],
        updated_by: str,
    ) -> None:
        self._archive_rows(
            select(ProjectStructureMember).where(
                ProjectStructureMember.project_id == project.id,
                ProjectStructureMember.side == side,
                ProjectStructureMember.archived_at.is_(None),
            ),
            updated_by,
        )
        for index, item in enumerate(items):
            role = self._text(item.get("role"))
            if not role:
                continue
            self.session.add(
                ProjectStructureMember(
                    project_id=project.id,
                    side=side,
                    role_title=role,
                    person_label=self._text(item.get("person")),
                    zone_text=self._text(item.get("zone")),
                    display_order=index,
                    updated_by=updated_by,
                )
            )

    def _replace_competitors(
        self,
        project: Project,
        side: str,
        items: list[dict[str, object]],
        updated_by: str,
    ) -> None:
        self._archive_rows(
            select(ProjectCompetitor).where(
                ProjectCompetitor.project_id == project.id,
                ProjectCompetitor.side == side,
                ProjectCompetitor.archived_at.is_(None),
            ),
            updated_by,
        )
        for index, item in enumerate(items):
            name = self._text(item.get("name"))
            if not name:
                continue
            self.session.add(
                ProjectCompetitor(
                    project_id=project.id,
                    side=side,
                    competitor_name=name,
                    strengths_text="\n".join(self._string_list(item.get("strengths"))),
                    weaknesses_text="\n".join(self._string_list(item.get("weaknesses"))),
                    display_order=index,
                    updated_by=updated_by,
                )
            )

    def _replace_swot(self, project: Project, value: dict[str, object], updated_by: str) -> None:
        self._archive_rows(
            select(ProjectSwotItem).where(
                ProjectSwotItem.project_id == project.id,
                ProjectSwotItem.archived_at.is_(None),
            ),
            updated_by,
        )
        for category in ("strengths", "weaknesses", "opportunities", "threats"):
            for index, item_text in enumerate(self._string_list(value.get(category))):
                self.session.add(
                    ProjectSwotItem(
                        project_id=project.id,
                        category=category,
                        item_text=item_text,
                        display_order=index,
                        updated_by=updated_by,
                    )
                )

    def _replace_interpretation_rules(
        self,
        project: Project,
        value: dict[str, object],
        updated_by: str,
    ) -> None:
        self._archive_rows(
            select(ProjectInterpretationRule).where(
                ProjectInterpretationRule.project_id == project.id,
                ProjectInterpretationRule.archived_at.is_(None),
            ),
            updated_by,
        )
        rules = value.get("rules")
        if isinstance(rules, list) and all(isinstance(item, str) for item in rules):
            for index, rule_text in enumerate(self._string_list(rules)):
                self.session.add(
                    ProjectInterpretationRule(
                        project_id=project.id,
                        rule_text=rule_text,
                        display_order=index,
                        updated_by=updated_by,
                    )
                )
            return

        for index, item in enumerate(self._record_items(value)):
            rule_text = self._text(item.get("rule"))
            if not rule_text:
                continue
            self.session.add(
                ProjectInterpretationRule(
                    project_id=project.id,
                    title=self._text(item.get("title")),
                    applies_to=self._text(item.get("appliesTo") or item.get("applies_to")),
                    rule_text=rule_text,
                    example_text=self._text(item.get("example")),
                    display_order=index,
                    updated_by=updated_by,
                )
            )

    def _replace_risk_map(
        self,
        project: Project,
        items: list[dict[str, object]],
        updated_by: str,
    ) -> None:
        self._archive_rows(
            select(ProjectRiskItem).where(
                ProjectRiskItem.project_id == project.id,
                ProjectRiskItem.archived_at.is_(None),
            ),
            updated_by,
        )
        for index, item in enumerate(items):
            title = self._text(item.get("title"))
            if not title:
                continue
            self.session.add(
                ProjectRiskItem(
                    project_id=project.id,
                    risk_title=title,
                    risk_type=self._text(item.get("barrier_type") or item.get("risk_type")),
                    probability_level=self._text(item.get("probability_level")),
                    probability_basis=self._text(item.get("probability_basis")),
                    impact_level=self._text(item.get("impact_level")),
                    impact_basis=self._text(item.get("impact_basis")),
                    related_to_text=self._text(item.get("related_to")),
                    early_signal_text=self._text(item.get("early_signal")),
                    control_action=self._text(item.get("control_action")),
                    control_owner=self._text(item.get("control_owner")),
                    review_period=self._text(item.get("review_period")),
                    source_text=self._text(item.get("source_text")),
                    display_order=index,
                    updated_by=updated_by,
                )
            )

    def _replace_summary(
        self,
        project: Project,
        title: str | None,
        value: dict[str, object],
        updated_by: str,
    ) -> None:
        state = project.summary_state
        if state is None or state.archived_at is not None:
            state = ProjectSummaryState(project_id=project.id)
            self.session.add(state)

        state.title = self._text(title) or self._text(value.get("title")) or "Ключевые выводы по проекту"
        state.note = self._text(value.get("note"))
        state.updated_by = updated_by

        self._archive_rows(
            select(ProjectSummaryItem).where(
                ProjectSummaryItem.project_id == project.id,
                ProjectSummaryItem.archived_at.is_(None),
            ),
            updated_by,
        )
        for group_key in ("critical_to_client", "main_risks"):
            for index, item_text in enumerate(self._string_list(value.get(group_key))):
                self.session.add(
                    ProjectSummaryItem(
                        project_id=project.id,
                        group_key=group_key,
                        item_text=item_text,
                        display_order=index,
                        updated_by=updated_by,
                    )
                )

    def _passport_block(
        self,
        project: Project,
        section_key: str,
        api_section: str,
        block_code: str,
        block_type: str,
        title: str,
    ) -> ProjectContextBlockRead | None:
        items = sorted(
            [
                item
                for item in project.passport_facts
                if item.section_key == section_key and item.archived_at is None
            ],
            key=lambda item: (item.display_order, item.label),
        )
        if not items:
            return None
        return ProjectContextBlockRead(
            section_key=api_section,
            block_code=block_code,
            block_type=block_type,
            title=title,
            content={
                "items": [{"label": item.label, "value": item.value} for item in items],
            },
            display_order=10,
            updated_at=self._max_updated_at(items, project.updated_at),
        )

    def _client_vision_block(self, project: Project) -> ProjectContextBlockRead | None:
        items = sorted(
            [item for item in project.client_vision_items if item.archived_at is None],
            key=lambda item: (item.display_order, item.title),
        )
        if not items:
            return None
        return ProjectContextBlockRead(
            section_key="client_vision",
            block_code="client_vision_001",
            block_type="records",
            title="Видение клиента",
            content={
                "items": [
                    {
                        "title": item.title,
                        "value": item.value_text,
                        "use": item.use_text or "",
                    }
                    for item in items
                ]
            },
            display_order=40,
            updated_at=self._max_updated_at(items, project.updated_at),
        )

    def _work_contours_block(self, project: Project) -> ProjectContextBlockRead | None:
        items = sorted(
            [item for item in project.work_contours if item.archived_at is None],
            key=lambda item: (item.display_order, item.contour_name),
        )
        if not items:
            return None
        return ProjectContextBlockRead(
            section_key="work_contours",
            block_code="work_contours_001",
            block_type="records",
            title="Контуры работы",
            content={
                "items": [
                    {
                        "contour": item.contour_name,
                        "owner": item.owner_role or "",
                        "text": item.description,
                    }
                    for item in items
                ]
            },
            display_order=50,
            updated_at=self._max_updated_at(items, project.updated_at),
        )

    def _project_history_block(self, project: Project) -> ProjectContextBlockRead | None:
        items = sorted(
            [item for item in project.history_events if item.archived_at is None],
            key=lambda item: (item.display_order, item.year_label, item.event_title),
        )
        if not items:
            return None
        return ProjectContextBlockRead(
            section_key="project_history",
            block_code="project_history_001",
            block_type="timeline",
            title="История проекта",
            content={
                "items": [
                    {
                        "year": item.year_label,
                        "title": item.event_title,
                        "text": item.description or "",
                    }
                    for item in items
                ]
            },
            display_order=60,
            updated_at=self._max_updated_at(items, project.updated_at),
        )

    def _need_pyramid_block(
        self,
        project: Project,
        side: str,
        section_key: str,
        block_code: str,
        title: str,
    ) -> ProjectContextBlockRead | None:
        items = sorted(
            [
                item
                for item in project.need_pyramid_items
                if item.side == side and item.archived_at is None
            ],
            key=lambda item: (item.display_order, item.level_label),
        )
        if not items:
            return None
        return ProjectContextBlockRead(
            section_key=section_key,
            block_code=block_code,
            block_type="pyramid",
            title=title,
            content={
                "items": [
                    {
                        "level": item.level_label,
                        "title": item.title,
                        "description": item.description or "",
                    }
                    for item in items
                ]
            },
            display_order=70 if side == "client" else 80,
            updated_at=self._max_updated_at(items, project.updated_at),
        )

    def _structure_block(
        self,
        project: Project,
        side: str,
        section_key: str,
        block_code: str,
        title: str,
    ) -> ProjectContextBlockRead | None:
        items = sorted(
            [
                item
                for item in project.structure_members
                if item.side == side and item.archived_at is None
            ],
            key=lambda item: (item.display_order, item.role_title),
        )
        if not items:
            return None
        return ProjectContextBlockRead(
            section_key=section_key,
            block_code=block_code,
            block_type="records",
            title=title,
            content={
                "items": [
                    {
                        "role": item.role_title,
                        "person": item.person_label or "",
                        "zone": item.zone_text or "",
                    }
                    for item in items
                ]
            },
            display_order=90 if side == "open" else 100,
            updated_at=self._max_updated_at(items, project.updated_at),
        )

    def _competitors_block(
        self,
        project: Project,
        side: str,
        section_key: str,
        block_code: str,
        title: str,
    ) -> ProjectContextBlockRead | None:
        items = sorted(
            [
                item
                for item in project.competitors
                if item.side == side and item.archived_at is None
            ],
            key=lambda item: (item.display_order, item.competitor_name),
        )
        if not items:
            return None
        return ProjectContextBlockRead(
            section_key=section_key,
            block_code=block_code,
            block_type="records",
            title=title,
            content={
                "items": [
                    {
                        "name": item.competitor_name,
                        "strengths": self._split_multiline(item.strengths_text),
                        "weaknesses": self._split_multiline(item.weaknesses_text),
                    }
                    for item in items
                ]
            },
            display_order=110 if side == "open" else 120,
            updated_at=self._max_updated_at(items, project.updated_at),
        )

    def _swot_block(self, project: Project) -> ProjectContextBlockRead | None:
        items = [item for item in project.swot_items if item.archived_at is None]
        if not items:
            return None
        grouped = {
            category: [
                item.item_text
                for item in sorted(
                    [value for value in items if value.category == category],
                    key=lambda value: (value.display_order, value.item_text),
                )
            ]
            for category in ("strengths", "weaknesses", "opportunities", "threats")
        }
        return ProjectContextBlockRead(
            section_key="swot",
            block_code="swot_001",
            block_type="swot",
            title="SWOT-анализ проекта",
            content=grouped,
            display_order=130,
            updated_at=self._max_updated_at(items, project.updated_at),
        )

    def _interpretation_rules_block(self, project: Project) -> ProjectContextBlockRead | None:
        items = sorted(
            [item for item in project.interpretation_rules if item.archived_at is None],
            key=lambda item: (item.display_order, item.rule_text),
        )
        if not items:
            return None
        return ProjectContextBlockRead(
            section_key="interpretation_rules",
            block_code="interpretation_rules_001",
            block_type="rules",
            title="Правила интерпретации",
            content={
                "rules": [item.rule_text for item in items],
                "items": [
                    {
                        "title": item.title or "",
                        "appliesTo": item.applies_to or "",
                        "rule": item.rule_text,
                        "example": item.example_text or "",
                    }
                    for item in items
                ],
            },
            display_order=140,
            updated_at=self._max_updated_at(items, project.updated_at),
        )

    def _risk_map_block(self, project: Project) -> ProjectContextBlockRead | None:
        items = sorted(
            [item for item in project.risk_items if item.archived_at is None],
            key=lambda item: (item.display_order, item.risk_title),
        )
        if not items:
            return None
        return ProjectContextBlockRead(
            section_key="risk_map",
            block_code="risk_map_001",
            block_type="risk_list",
            title="Карта рисков",
            content={
                "items": [
                    {
                        "title": item.risk_title,
                        "barrier_type": item.risk_type or "",
                        "probability_level": item.probability_level or "",
                        "probability_basis": item.probability_basis or "",
                        "impact_level": item.impact_level or "",
                        "impact_basis": item.impact_basis or "",
                        "related_to": item.related_to_text or "",
                        "early_signal": item.early_signal_text or "",
                        "control_action": item.control_action or "",
                        "control_owner": item.control_owner or "",
                        "review_period": item.review_period or "",
                        "source_text": item.source_text or "",
                    }
                    for item in items
                ]
            },
            display_order=150,
            updated_at=self._max_updated_at(items, project.updated_at),
        )

    def _summary_block(self, project: Project) -> ProjectContextBlockRead | None:
        items = [item for item in project.summary_items if item.archived_at is None]
        state = project.summary_state if project.summary_state and project.summary_state.archived_at is None else None
        if not items and state is None:
            return None
        return ProjectContextBlockRead(
            section_key="summary",
            block_code="summary_001",
            block_type="management_summary",
            title=state.title if state and state.title else "Ключевые выводы по проекту",
            content={
                "critical_to_client": [
                    item.item_text
                    for item in sorted(
                        [value for value in items if value.group_key == "critical_to_client"],
                        key=lambda value: (value.display_order, value.item_text),
                    )
                ],
                "main_risks": [
                    item.item_text
                    for item in sorted(
                        [value for value in items if value.group_key == "main_risks"],
                        key=lambda value: (value.display_order, value.item_text),
                    )
                ],
                "note": state.note if state else "",
            },
            display_order=160,
            updated_at=self._max_updated_at(
                [*items, state] if state else items,
                project.updated_at,
            ),
        )

    def _archive_rows(self, statement: Any, updated_by: str) -> None:
        rows = list(self.session.scalars(statement).all())
        for row in rows:
            row.archived_at = datetime.now(timezone.utc)
            row.archived_by = updated_by
            row.updated_by = updated_by

    def _record_items(self, content: dict[str, object]) -> list[dict[str, object]]:
        items = content.get("items")
        if not isinstance(items, list):
            return []
        return [item for item in items if isinstance(item, dict)]

    def _string_list(self, value: object) -> list[str]:
        if isinstance(value, str):
            return [line.strip() for line in value.splitlines() if line.strip()]
        if not isinstance(value, list):
            return []
        return [str(item).strip() for item in value if str(item).strip()]

    def _split_multiline(self, value: str | None) -> list[str]:
        return [line.strip() for line in (value or "").splitlines() if line.strip()]

    def _text(self, value: object) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _max_updated_at(self, values: list[object], fallback: datetime) -> datetime:
        timestamps = [getattr(value, "updated_at", None) for value in values]
        valid = [value for value in timestamps if isinstance(value, datetime)]
        return max(valid, default=fallback)
