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
        return self.session.scalar(select(Project).where(Project.project_code == project_code))

    def get_goal(self, project_id: object, goal_code: str) -> ProjectGoal | None:
        return self.session.scalar(
            select(ProjectGoal).where(
                ProjectGoal.project_id == project_id,
                ProjectGoal.source_id == goal_code,
            )
        )

    def get_lpr(self, project_id: object, lpr_code: str) -> LPRProfile | None:
        return self.session.scalar(
            select(LPRProfile).where(
                LPRProfile.project_id == project_id,
                LPRProfile.lpr_code == lpr_code,
            )
        )

    def get_barrier(self, project_id: object, barrier_code: str) -> ProjectBarrier | None:
        return self.session.scalar(
            select(ProjectBarrier).where(
                ProjectBarrier.project_id == project_id,
                ProjectBarrier.source_id == barrier_code,
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
            )
        )

    def get_kpi(self, project_id: object, kpi_code: str) -> ProjectKPI | None:
        return self.session.scalar(
            select(ProjectKPI).where(
                ProjectKPI.project_id == project_id,
                ProjectKPI.kpi_code == kpi_code,
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
            )
        )

    def save(self, entity: object) -> None:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
