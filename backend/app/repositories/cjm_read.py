from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.cjm import CommunicationPoint, ProjectBarrier
from app.models.lpr import LPRProfile
from app.models.project import ClientExpectation, Project, ProjectGoal, ProjectKPI


class CJMReadRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_projects(self) -> list[Project]:
        return list(
            self.session.scalars(
                select(Project)
                .where(Project.archived_at.is_(None))
                .order_by(Project.project_code)
            ).all()
        )

    def get_project_by_code(self, project_code: str) -> Project | None:
        return self.session.scalar(
            select(Project).where(
                Project.project_code == project_code,
                Project.archived_at.is_(None),
            )
        )

    def list_lprs(self, project_id: object) -> list[LPRProfile]:
        statement = (
            select(LPRProfile)
            .options(selectinload(LPRProfile.importance_factors))
            .where(
                LPRProfile.project_id == project_id,
                LPRProfile.archived_at.is_(None),
            )
            .order_by(LPRProfile.lpr_code)
        )
        return list(self.session.scalars(statement).all())

    def list_barriers(self, project_id: object) -> list[ProjectBarrier]:
        statement = (
            select(ProjectBarrier)
            .where(
                ProjectBarrier.project_id == project_id,
                ProjectBarrier.archived_at.is_(None),
            )
            .order_by(ProjectBarrier.source_id, ProjectBarrier.barrier_title)
        )
        return list(self.session.scalars(statement).all())

    def list_expectations(self, project_id: object) -> list[ClientExpectation]:
        statement = (
            select(ClientExpectation)
            .where(
                ClientExpectation.project_id == project_id,
                ClientExpectation.archived_at.is_(None),
            )
            .order_by(ClientExpectation.source_id, ClientExpectation.expectation_text)
        )
        return list(self.session.scalars(statement).all())

    def list_kpis(self, project_id: object) -> list[ProjectKPI]:
        statement = (
            select(ProjectKPI)
            .where(
                ProjectKPI.project_id == project_id,
                ProjectKPI.archived_at.is_(None),
            )
            .order_by(ProjectKPI.kpi_code)
        )
        return list(self.session.scalars(statement).all())

    def list_communications(self, project_id: object) -> list[CommunicationPoint]:
        statement = (
            select(CommunicationPoint)
            .where(
                CommunicationPoint.project_id == project_id,
                CommunicationPoint.archived_at.is_(None),
            )
            .order_by(CommunicationPoint.source_id, CommunicationPoint.summary)
        )
        return list(self.session.scalars(statement).all())

    def list_goals(self, project_id: object) -> list[ProjectGoal]:
        statement = (
            select(ProjectGoal)
            .where(
                ProjectGoal.project_id == project_id,
                ProjectGoal.archived_at.is_(None),
            )
            .order_by(ProjectGoal.source_id, ProjectGoal.goal_text)
        )
        return list(self.session.scalars(statement).all())
