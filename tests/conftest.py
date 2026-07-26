from __future__ import annotations

from pathlib import Path

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

from app.config import load_settings, reset_settings_cache


@pytest.fixture
def env_setup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("APP_SECRET_KEY", "test-secret")
    monkeypatch.setenv("APP_ENCRYPTION_KEY", Fernet.generate_key().decode())
    monkeypatch.setenv("BOOTSTRAP_ADMIN_USERNAME", "admin")
    monkeypatch.setenv("BOOTSTRAP_ADMIN_PASSWORD", "password123")
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("SCHEDULER_ENABLED", "false")
    reset_settings_cache()
    yield
    reset_settings_cache()


@pytest.fixture
def client(env_setup):
    from app.main import create_app

    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


def login(client: TestClient):
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "password123"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    return response
