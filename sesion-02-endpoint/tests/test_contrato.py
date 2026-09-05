"""El contrato, en pruebas.

Estas pruebas no llaman al modelo: reemplazan `triar` por una función que
devuelve lo que se le pida. Así corren en un segundo, sin clave y sin gastar
un token, y comprueban lo único que promete el contrato — qué códigos devuelve
el servicio y cuándo.

    pytest tests/ -q

La prueba que sí llama al proveedor es otra cosa y llega en la sesión 5, con
el conjunto de evaluación.
"""

import os

import pytest
from fastapi.testclient import TestClient

# Las claves se ponen antes de importar la aplicación, porque `app.modelo`
# construye el cliente del proveedor al importarse. Son de mentira: ninguna
# de estas pruebas sale a la red.
os.environ.setdefault("OPENROUTER_API_KEY", "sk-or-v1-de-prueba")
os.environ.setdefault("API_KEY", "clave-de-prueba")

from app import main  # noqa: E402

CLAVE = {"X-API-Key": "clave-de-prueba"}
BIEN = {"area": "facturacion", "urgencia": "alta", "confianza": 0.9,
        "evidencia": "Me cobraron dos veces"}


@pytest.fixture
def cliente(monkeypatch):
    monkeypatch.setattr(main, "triar", lambda texto: BIEN)
    return TestClient(main.app)


def test_salud_no_pide_clave(cliente):
    assert cliente.get("/salud").json() == {"estado": "ok"}


def test_sin_cabecera_devuelve_401(cliente):
    r = cliente.post("/reclamos", json={"id": "RCL-1", "texto": "hola", "canal": "correo"})
    assert r.status_code == 401


def test_texto_vacio_devuelve_422(cliente):
    r = cliente.post("/reclamos", headers=CLAVE,
                     json={"id": "RCL-1", "texto": "", "canal": "correo"})
    assert r.status_code == 422


def test_canal_fuera_de_la_lista_devuelve_422(cliente):
    r = cliente.post("/reclamos", headers=CLAVE,
                     json={"id": "RCL-1", "texto": "hola", "canal": "paloma"})
    assert r.status_code == 422


def test_reclamo_valido_devuelve_la_salida_del_contrato(cliente):
    r = cliente.post("/reclamos", headers=CLAVE,
                     json={"id": "RCL-1", "texto": "Me cobraron dos veces", "canal": "correo"})
    assert r.status_code == 200
    assert set(r.json()) == {"area", "urgencia", "confianza", "evidencia"}


def test_factura_que_el_erp_no_tiene_devuelve_409(cliente):
    r = cliente.post("/reclamos", headers=CLAVE,
                     json={"id": "RCL-1", "texto": "Reclamo la factura 99-9999",
                           "canal": "correo"})
    assert r.status_code == 409


def test_factura_que_existe_pasa(cliente):
    r = cliente.post("/reclamos", headers=CLAVE,
                     json={"id": "RCL-1", "texto": "Reclamo la factura 88-4412",
                           "canal": "correo"})
    assert r.status_code == 200


def test_salida_que_no_cumple_el_esquema_devuelve_422(cliente, monkeypatch):
    monkeypatch.setattr(main, "triar", lambda texto: {"area": "inventada"})
    r = cliente.post("/reclamos", headers=CLAVE,
                     json={"id": "RCL-1", "texto": "hola", "canal": "correo"})
    assert r.status_code == 422
