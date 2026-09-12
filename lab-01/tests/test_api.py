from types import SimpleNamespace

import pytest

from servicio.contratos import Clasificacion








def test_salud_y_documentacion_son_publicas(cliente):
    assert cliente.get("/salud").json() == {"estado": "ok"}
    assert cliente.get("/docs").status_code == 200


def test_rutas_api_exigen_credencial(cliente):
    assert cliente.post("/api/clasificar", json={"mensaje": "hola"}).status_code == 401






def test_clasificacion_respeta_contrato(cliente, headers, monkeypatch):
    async def clasificar_falso(_):
        return Clasificacion(intencion="devolucion", sentimiento="negativo",
                             urgencia="alta", evidencia="producto distinto")

    monkeypatch.setattr("servicio.main.clasificar", clasificar_falso)
    respuesta = cliente.post("/api/clasificar", headers=headers,
                             json={"mensaje": "Recibí un producto distinto"})
    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "intencion": "devolucion", "sentimiento": "negativo",
        "urgencia": "alta", "evidencia": "producto distinto",
    }


def test_error_de_proveedor_es_503(cliente, headers, monkeypatch):
    async def falla(_):
        raise RuntimeError("proveedor no disponible")

    monkeypatch.setattr("servicio.main.clasificar", falla)
    respuesta = cliente.post("/api/clasificar", headers=headers, json={"mensaje": "hola"})
    assert respuesta.status_code == 503
