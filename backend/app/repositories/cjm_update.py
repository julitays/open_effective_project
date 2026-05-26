from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cjm import CommunicationPoint, ProjectBarrier
from app.models.lpr import LPRProfile
from app.models.project import ClientExpectation, Project, ProjectGoal, ProjectKPI


class CJMUpdateRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_project(self, project_code: str) -> Project | None:
        return self.session.scalar(
            select(Project).where(
                Project.project_code == project_code,
                Project.archived_at.is_(None),
            )
        )

    def get_project_by_external_id(self, external_project_id: str) -> Project | None:
        return self.session.scalar(
            select(Project).where(
                Project.external_project_id == external_project_id,
            )
        )

    def get_goal(self, project_id: object, goal_code: str) -> ProjectGoal | None:
        return self.session.scalar(
            select(ProjectGoal).where(
                ProjectGoal.project_id == project_id,
                ProjectGoal.source_id == goal_code,
                ProjectGoal.archived_at.is_(None),
            )
        )

    def get_lpr(self, project_id: object, lpr_code: str) -> LPRProfile | None:
        return self.session.scalar(
            select(LPRProfile).where(
                LPRProfile.project_id == project_id,
                LPRProfile.lpr_code == lpr_code,
                LPRProfile.archived_at.is_(None),
            )
        )

    def list_lprs(self, project_id: object) -> list[LPRProfile]:
        return list(
            self.session.scalars(
                select(LPRProfile).where(
                    LPRProfile.project_id == project_id,
                    LPRProfile.archived_at.is_(None),
                )
            ).all()
        )

    def get_barrier(self, project_id: object, barrier_code: str) -> ProjectBarrier | None:
        return self.session.scalar(
            select(ProjectBarrier).where(
                ProjectBarrier.project_id == project_id,
                ProjectBarrier.source_id == barrier_code,
                ProjectBarrier.archived_at.is_(None),
            )
        )

    def get_expectation(
        self,
        project_id: object,
        expectation_code: str,
    ) -> ClientExpectation | None:
        return self.session.scalar(
            select(ClientExpectation).where(
                ClientExpectation.project_id == project_id,
                ClientExpectation.source_id == expectation_code,
                ClientExpectation.archived_at.is_(None),
            )
        )

    def get_kpi(self, project_id: object, kpi_code: str) -> ProjectKPI | None:
        return self.session.scalar(
            select(ProjectKPI).where(
                ProjectKPI.project_id == project_id,
                ProjectKPI.kpi_code == kpi_code,
                ProjectKPI.archived_at.is_(None),
            )
        )

    def get_communication(
        self,
        project_id: object,
        communication_code: str,
    ) -> CommunicationPoint | None:
        return self.session.scalar(
            select(CommunicationPoint).where(
                CommunicationPoint.project_id == project_id,
                CommunicationPoint.source_id == communication_code,
                CommunicationPoint.archived_at.is_(None),
            )
        )

    def list_codes(self, project_id: object, entity: str) -> list[str]:
        code_columns = {
            "goal": (ProjectGoal, ProjectGoal.source_id),
            "lpr": (LPRProfile, LPRProfile.lpr_code),
            "barrier": (ProjectBarrier, ProjectBarrier.source_id),
            "expectation": (ClientExpectation, ClientExpectation.source_id),
            "kpi": (ProjectKPI, ProjectKPI.kpi_code),
            "communication": (CommunicationPoint, CommunicationPoint.source_id),
        }
        model, column = code_columns[entity]
        return [
            code
            for code in self.session.scalars(
                select(column).where(model.project_id == project_id)
            ).all()
            if code
        ]

    def list_project_codes(self) -> list[str]:
        return [code for code in self.session.scalars(select(Project.project_code)).all() if code]

    def save(self, entity: object) -> None:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
