from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.db import get_db
from app.core.demo_auth import create_session_token
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
            project_scale="regional",
            known_regions="Region A; Region B",
            primary_operational_model="merchandising",
            additional_operational_contours="training",
            current_phase="development",
            status="active",
            start_date="2026",
            short_description="Anonymized project summary",
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
            activity_status="active",
            relationship_status="positive",
            evidence_basis="Restored CJM",
            manual_comment="Check role later",
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
                    source_text="Restored CJM",
                    evidence_quote="Anonymized evidence",
                    period_or_source="2026",
                    confidence_level="high",
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
                    description="Barrier description",
                    linked_kpi_text="scorecard; execution quality",
                    related_lpr_code="lpr_007",
                    external_lpr_id="845; 55",
                    related_importance_text="безопасность",
                    source_text="Restored CJM",
                    evidence_quote="Barrier evidence",
                    first_seen_period="2025",
                    last_seen_period="2026",
                    relevance_status="current",
                    confidence_level="high",
                ),
                ClientExpectation(
                    project_id=project.id,
                    source_id="expectation_001",
                    expectation_text="Stable quality",
                    expectation_type="quality",
                    explicitness="explicit",
                    criticality="high",
                    linked_kpi_text="OSA; ISA",
                    related_lpr_code="lpr_007",
                    external_lpr_id="845; 55",
                    related_importance_text="качество исполнения",
                    source_text="Restored CJM",
                    evidence_quote="Expectation evidence",
                    relevance_status="current",
                    confidence_level="high",
                ),
                ProjectKPI(
                    project_id=project.id,
                    kpi_code="kpi_001",
                    metric_name="Execution quality",
                    kpi_type="service",
                    source_text="Restored CJM",
                    relevance_status="current",
                    related_expectation_text="expectation_001",
                    related_barrier_text="barrier_001",
                    client_criticality="high",
                    comment="KPI note",
                    requires_confirmation="no",
                    status="tracked",
                ),
                CommunicationPoint(
                    project_id=project.id,
                    source_id="communication_001",
                    point_type="meeting",
                    client_side="lpr_007",
                    external_lpr_id="845; 55",
                    open_side_role="Project role",
                    topic_text="Project status",
                    channel_text="Встреча",
                    frequency="weekly",
                    criticality="high",
                    source_text="Restored CJM",
                    relevance_status="current",
                    comment="Communication note",
                    summary="Project status meeting",
                ),
                ProjectGoal(
                    project_id=project.id,
                    source_id="goal_001",
                    goal_text="Keep delivery quality",
                    goal_type="service",
                    goal_owner="Project role",
                    priority="high",
                    related_kpi_or_criterion_text="kpi_001",
                    source_text="Restored CJM",
                    relevance_status="current",
                    comment="Goal note",
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
            "project_scale": "regional",
            "known_regions": "Region A; Region B",
            "primary_operational_model": "merchandising",
            "additional_operational_contours": "training",
            "lifecycle_stage": "development",
            "project_status": "active",
            "start_date": "2026",
            "short_description": "Anonymized project summary",
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
            "role_zone": "Regional role",
            "influence_level": "high",
            "activity_status": "active",
            "relationship_status": "positive",
            "evidence_basis": "Restored CJM",
            "manual_comment": "Check role later",
            "importance_factors": [
                {
                    "factor_type": "safety",
                    "factor_text": "безопасность",
                    "criticality": "high",
                    "source_type": "manual_excel",
                    "source_text": "Restored CJM",
                    "evidence_quote": "Anonymized evidence",
                    "period_or_source": "2026",
                    "confidence_level": "high",
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
    assert barriers.json()[0]["relevance_status"] == "current"
    assert barriers.json()[0]["confidence_level"] == "high"
    assert barriers.json()[0]["source_text"] == "Restored CJM"
    assert barriers.json()[0]["evidence_quote"] == "Barrier evidence"
    assert expectations.json()[0]["linked_kpi_text"] == "OSA; ISA"
    assert expectations.json()[0]["relevance_status"] == "current"
    assert expectations.json()[0]["confidence_level"] == "high"
    assert expectations.json()[0]["source_text"] == "Restored CJM"


def test_patch_project_updates_only_passed_fields(cjm_client: TestClient) -> None:
    response = cjm_client.patch(
        "/api/v1/projects/project_001",
        json={"short_description": "Updated summary"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["short_description"] == "Updated summary"
    assert payload["known_regions"] == "Region A; Region B"


def test_patch_goal_works(cjm_client: TestClient) -> None:
    response = cjm_client.patch(
        "/api/v1/projects/project_001/goals/goal_001",
        json={"goal_text": "Updated goal", "relevance_status": "Требует подтверждения"},
    )

    assert response.status_code == 200
    assert response.json()["goal_text"] == "Updated goal"
    assert response.json()["relevance_status"] == "requires_confirmation"


def test_patch_barrier_works(cjm_client: TestClient) -> None:
    response = cjm_client.patch(
        "/api/v1/projects/project_001/barriers/barrier_001",
        json={"barrier_title": "Updated barrier", "time_status": "Повторяется"},
    )

    assert response.status_code == 200
    assert response.json()["barrier_title"] == "Updated barrier"
    assert response.json()["time_status"] == "repeated"


def test_patch_unknown_entity_returns_404(cjm_client: TestClient) -> None:
    response = cjm_client.patch(
        "/api/v1/projects/project_001/barriers/barrier_missing",
        json={"barrier_title": "Updated barrier"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Barrier 'barrier_missing' was not found."


def test_patch_without_auth_returns_401_when_demo_auth_enabled(
    cjm_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "DEMO_AUTH_ENABLED", True)
    monkeypatch.setattr(settings, "DEMO_AUTH_USERNAME", "demo")
    monkeypatch.setattr(settings, "DEMO_AUTH_PASSWORD", "correct-password")
    monkeypatch.setattr(settings, "SECRET_KEY", "test-secret-key")
    monkeypatch.setattr(settings, "SESSION_COOKIE_NAME", "test_session")
    monkeypatch.setattr(settings, "SESSION_TTL_SECONDS", 3600)

    response = cjm_client.patch(
        "/api/v1/projects/project_001",
        json={"short_description": "Should not update"},
    )

    assert response.status_code == 401


def test_patch_with_auth_works(
    cjm_client: TestClient,
    cjm_session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "DEMO_AUTH_ENABLED", True)
    monkeypatch.setattr(settings, "DEMO_AUTH_USERNAME", "demo")
    monkeypatch.setattr(settings, "DEMO_AUTH_PASSWORD", "correct-password")
    monkeypatch.setattr(settings, "SECRET_KEY", "test-secret-key")
    monkeypatch.setattr(settings, "SESSION_COOKIE_NAME", "test_session")
    monkeypatch.setattr(settings, "SESSION_TTL_SECONDS", 3600)
    cjm_client.cookies.set(settings.SESSION_COOKIE_NAME, create_session_token("demo"))

    response = cjm_client.patch(
        "/api/v1/projects/project_001",
        json={"short_description": "Updated with auth"},
    )

    assert response.status_code == 200
    assert response.json()["short_description"] == "Updated with auth"
    with cjm_session_factory() as session:
        project = session.scalar(select(Project).where(Project.project_code == "project_001"))
        assert project is not None
        assert project.updated_by == "demo"


def test_local_cors_allows_patch_preflight(cjm_client: TestClient) -> None:
    response = cjm_client.options(
        "/api/v1/projects/project_001",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "PATCH",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert "PATCH" in response.headers["access-control-allow-methods"]
