from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from servicio.main import app




@pytest.fixture
def cliente(monkeypatch):
    monkeypatch.setenv("API_KEY", "clave-prueba")
    monkeypatch.setenv("PROPUESTA_SECRET", "secreto-prueba-largo")
    monkeypatch.setenv("CLIENTE_DEMO", "C-001")
    monkeypatch.setenv("LANGFUSE_ENABLED", "false")
    monkeypatch.delenv("K_SERVICE", raising=False)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def headers():
    return {"X-API-Key": "clave-prueba"}
