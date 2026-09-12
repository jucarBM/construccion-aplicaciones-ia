from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from servicio import crm
from servicio.main import app


@pytest.fixture
def crm_aislado(tmp_path: Path, monkeypatch):
    carpeta = tmp_path / "crm"
    carpeta.mkdir()
    carpeta.joinpath("pedidos.txt").write_text(
        "pedido_id | cliente_id | fecha | fecha_entrega | estado | producto | entregado\n"
        "P-1042 | C-001 | 2026-09-01 | 2026-09-04 | entregado | Audífonos negros | si\n"
        "P-1043 | C-001 | 2026-09-05 |  | en_transito | Taza azul | no\n"
        "P-2099 | C-OTRO | 2026-09-02 | 2026-09-05 | entregado | Mochila verde | si\n",
        encoding="utf-8",
    )
    carpeta.joinpath("politicas.txt").write_text(
        "tipo | dias | condiciones\n"
        "devolucion | 30 | Producto sin uso indebido; sujeto a revisión.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(crm, "CARPETA_CRM", carpeta)
    monkeypatch.delenv("CRM_BUCKET", raising=False)
    return carpeta


@pytest.fixture
def cliente(monkeypatch, crm_aislado):
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
