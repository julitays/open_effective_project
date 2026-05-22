from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sqlalchemy import func, select

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.db import SessionLocal  # noqa: E402
from app.models import (  # noqa: E402
    ClientExpectation,
    CommunicationPoint,
    LPRImportanceFactor,
    LPRProfile,
    Project,
    ProjectBarrier,
    ProjectGoal,
    ProjectKPI,
)


def _count(session: object, model: object, project_id: object) -> int:
    return int(
        session.scalar(  # type: ignore[attr-defined]
            select(func.count()).select_from(model).where(model.project_id == project_id)
        )
        or 0
    )


def _value(value: object) -> str:
    return str(value) if value not in (None, "") else "-"


def main() -> int:
    parser = argparse.ArgumentParser(description="Read back imported CJM MVP project rows.")
    parser.add_argument("--project", required=True, help="Anonymized project code, e.g. project_001.")
    args = parser.parse_args()

    with SessionLocal() as session:
        project = session.scalar(select(Project).where(Project.project_code == args.project))
        if project is None:
            print("Project found: no")
            print(f"Project code: {args.project}")
            return 1

        print("Project found: yes")
        print(f"Project code: {project.project_code}")
        print(f"external_project_id: {_value(project.external_project_id)}")
        print(f"LPR profiles: {_count(session, LPRProfile, project.id)}")
        print(f"LPR importance factors: {_count(session, LPRImportanceFactor, project.id)}")
        print(
            "LPR importance factors mapped as other: "
            f"{session.scalar(select(func.count()).select_from(LPRImportanceFactor).where(LPRImportanceFactor.project_id == project.id, LPRImportanceFactor.factor_type == 'other')) or 0}"
        )
        print(f"Barriers: {_count(session, ProjectBarrier, project.id)}")
        print(f"Expectations: {_count(session, ClientExpectation, project.id)}")
        print(f"KPIs: {_count(session, ProjectKPI, project.id)}")
        print(f"Communication points: {_count(session, CommunicationPoint, project.id)}")
        print(f"Goals: {_count(session, ProjectGoal, project.id)}")

        print("")
        print("LPR IDs | external LPR IDs")
        for lpr in session.scalars(
            select(LPRProfile)
            .where(LPRProfile.project_id == project.id)
            .order_by(LPRProfile.lpr_code)
        ):
            print(f"- {lpr.lpr_code} | {_value(lpr.external_lpr_id)}")

        print("")
        print("Barrier ID | title | linked_kpi_text")
        for barrier in session.scalars(
            select(ProjectBarrier)
            .where(ProjectBarrier.project_id == project.id)
            .order_by(ProjectBarrier.source_id, ProjectBarrier.barrier_title)
        ):
            print(
                f"- {_value(barrier.source_id)} | {barrier.barrier_title} | "
                f"{_value(barrier.linked_kpi_text)}"
            )

        print("")
        print("Expectation ID | title | linked_kpi_text")
        for expectation in session.scalars(
            select(ClientExpectation)
            .where(ClientExpectation.project_id == project.id)
            .order_by(ClientExpectation.source_id, ClientExpectation.expectation_text)
        ):
            print(
                f"- {_value(expectation.source_id)} | {expectation.expectation_text} | "
                f"{_value(expectation.linked_kpi_text)}"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
