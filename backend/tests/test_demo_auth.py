from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.db import get_db
from app.main import app
from app.models import Base, Project


@pytest.fixture()
def auth_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "DEMO_AUTH_ENABLED", True)
    monkeypatch.setattr(settings, "DEMO_AUTH_USERNAME", "demo")
    monkeypatch.setattr(settings, "DEMO_AUTH_PASSWORD", "correct-password")
    monkeypatch.setattr(settings, "SECRET_KEY", "test-secret-key")
    monkeypatch.setattr(settings, "SESSION_COOKIE_NAME", "test_session")
    monkeypatch.setattr(settings, "SESSION_TTL_SECONDS", 3600)
    monkeypatch.setattr(settings, "ENV", "test")


@pytest.fixture()
def auth_session_factory() -> Generator[sessionmaker[Session], None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    with session_factory() as session:
        session.add(
            Project(
                project_code="project_001",
                external_project_id="external_project_001",
                project_type="fmcg",
                project_scale="regional",
                primary_operational_model="merchandising",
                current_phase="development",
                status="active",
                short_description="Anonymized project summary",
            )
        )
        session.commit()

    yield session_factory
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def auth_client(
    auth_session_factory: sessionmaker[Session],
) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        db = auth_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_health_endpoint_is_public_with_demo_auth(auth_settings: None) -> None:
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_protected_api_returns_401_without_session(auth_settings: None) -> None:
    client = TestClient(app)

    response = client.get("/api/v1/projects")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required."


def test_login_with_wrong_password_does_not_create_session(
    auth_settings: None,
) -> None:
    client = TestClient(app)

    response = client.post(
        "/login",
        data={"username": "demo", "password": "wrong-password"},
        follow_redirects=False,
    )

    assert response.status_code == 401
    assert settings.SESSION_COOKIE_NAME not in response.cookies
    assert "Неверный логин или пароль" in response.text


def test_login_with_valid_credentials_creates_session(auth_settings: None) -> None:
    client = TestClient(app)

    response = client.post(
        "/login",
        data={"username": "demo", "password": "correct-password"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert settings.SESSION_COOKIE_NAME in response.cookies
    assert "httponly" in response.headers["set-cookie"].lower()


def test_protected_api_is_available_with_valid_session(
    auth_settings: None,
    auth_client: TestClient,
) -> None:
    login_response = auth_client.post(
        "/login",
        data={"username": "demo", "password": "correct-password"},
        follow_redirects=False,
    )

    assert login_response.status_code == 303
    response = auth_client.get("/api/v1/projects")

    assert response.status_code == 200
    assert response.json()[0]["project_code"] == "project_001"


def test_demo_auth_disabled_does_not_block_api(
    monkeypatch: pytest.MonkeyPatch,
    auth_client: TestClient,
) -> None:
    monkeypatch.setattr(settings, "DEMO_AUTH_ENABLED", False)

    response = auth_client.get("/api/v1/projects")

    assert response.status_code == 200
    assert response.json()[0]["project_code"] == "project_001"
