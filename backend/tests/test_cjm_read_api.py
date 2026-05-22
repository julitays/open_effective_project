from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.db import get_db
from app.main import app
from app.models import (
    Base,
    ClientExpectation,
    CommunicationPoint,
    LPRImportanceFactor,
    LPRProfile,
    Project,
    ProjectBarrier,
    ProjectGoal,
    ProjectKPI,
)
from app.repositories.cjm_read import CJMReadRepository
from app.services.cjm_read import CJMReadService


def _seed_project(session_factory: sessionmaker[Session]) -> None:
    with session_factory() as session:
        project = Project(
            project_code="project_001",
            external_project_id="external_project_001",
            working_project_code="working_project_001",
            project_type="fmcg",
            current_phase="development",
            status="active",
        )
        session.add(project)
        session.flush()

        lpr = LPRProfile(
            project_id=project.id,
            lpr_code="lpr_007",
            external_lpr_id="845; 55",
            stakeholder_role="Regional role",
            influence_level="high",
            engagement_status="active",
        )
        session.add(lpr)
        session.flush()

        session.add_all(
            [
                LPRImportanceFactor(
                    project_id=project.id,
                    lpr_id=lpr.id,
                    factor_type="safety",
                    factor_text="безопасность",
                    importance_level="high",
                    source_type="manual_excel",
                ),
                ProjectBarrier(
                    project_id=project.id,
                    barrier_title="Execution risk",
                    barrier_type="execution_quality",
                    time_status="current",
                    criticality="high",
                    status="open",
                    source_type="manual_excel",
                    source_id="barrier_001",
                    linked_kpi_text="scorecard; execution quality",
                ),
                ClientExpectation(
                    project_id=project.id,
                    source_id="expectation_001",
                    expectation_text="Stable quality",
                    expectation_type="quality",
                    explicitness="explicit",
                    criticality="high",
                    linked_kpi_text="OSA; ISA",
                ),
                ProjectKPI(
                    project_id=project.id,
                    kpi_code="kpi_001",
                    metric_name="Execution quality",
                    status="tracked",
                ),
                CommunicationPoint(
                    project_id=project.id,
                    source_id="communication_001",
                    point_type="meeting",
                    summary="Project status meeting",
                ),
                ProjectGoal(
                    project_id=project.id,
                    source_id="goal_001",
                    goal_text="Keep delivery quality",
                    goal_type="service",
                    status="open",
                ),
            ]
        )
        session.commit()


@pytest.fixture()
def cjm_session_factory() -> Generator[sessionmaker[Session], None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    _seed_project(session_factory)
    yield session_factory
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def cjm_client(
    cjm_session_factory: sessionmaker[Session],
) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        db = cjm_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_projects_endpoint_returns_list(cjm_client: TestClient) -> None:
    response = cjm_client.get("/api/v1/projects")

    assert response.status_code == 200
    assert response.json() == [
        {
            "project_code": "project_001",
            "external_project_id": "external_project_001",
            "working_project_code": "working_project_001",
            "direction": "fmcg",
            "project_scale": None,
            "lifecycle_stage": "development",
            "project_status": "active",
            "short_description": None,
        }
    ]


def test_unknown_project_returns_404(cjm_client: TestClient) -> None:
    response = cjm_client.get("/api/v1/projects/project_missing")

    assert response.status_code == 404
    assert response.json()["detail"] == "CJM project 'project_missing' was not found."


def test_cjm_service_assembles_project(
    cjm_session_factory: sessionmaker[Session],
) -> None:
    with cjm_session_factory() as session:
        cjm = CJMReadService(CJMReadRepository(session)).get_project_cjm("project_001")

    assert cjm is not None
    assert cjm.project.project_code == "project_001"
    assert cjm.lprs[0].external_lpr_id == "845; 55"
    assert cjm.lprs[0].importance_factors[0].factor_type == "safety"


def test_composite_cjm_endpoint_contains_frontend_sections(cjm_client: TestClient) -> None:
    response = cjm_client.get("/api/v1/projects/project_001/cjm")

    assert response.status_code == 200
    assert set(response.json()) == {
        "project",
        "goals",
        "lprs",
        "barriers",
        "expectations",
        "kpis",
        "communications",
    }


def test_lpr_read_does_not_duplicate_external_aliases(cjm_client: TestClient) -> None:
    response = cjm_client.get("/api/v1/projects/project_001/lprs")

    assert response.status_code == 200
    assert response.json() == [
        {
            "lpr_code": "lpr_007",
            "external_lpr_id": "845; 55",
            "role": "Regional role",
            "influence_level": "high",
            "activity_status": "active",
            "relationship_status": None,
            "importance_factors": [
                {
                    "factor_type": "safety",
                    "factor_text": "безопасность",
                    "criticality": "high",
                    "source_type": "manual_excel",
                }
            ],
        }
    ]


def test_linked_kpi_text_is_read_for_barriers_and_expectations(cjm_client: TestClient) -> None:
    barriers = cjm_client.get("/api/v1/projects/project_001/barriers")
    expectations = cjm_client.get("/api/v1/projects/project_001/expectations")

    assert barriers.status_code == 200
    assert expectations.status_code == 200
    assert barriers.json()[0]["linked_kpi_text"] == "scorecard; execution quality"
    assert expectations.json()[0]["linked_kpi_text"] == "OSA; ISA"
