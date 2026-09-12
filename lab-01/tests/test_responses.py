"""Pruebas del SDK contra un transporte HTTP local, sin proveedor ni credenciales."""
import asyncio
import json

import httpx
import pytest
from openai import AsyncOpenAI

from servicio import llm


def respuesta_http(texto, output=None, status="completed"):
    return {"id": "resp_prueba", "object": "response", "created_at": 0,
            "model": "gpt-4o-mini", "status": status,
            "parallel_tool_calls": False, "tool_choice": "auto", "tools": [],
            "output": output if output is not None else [{
                "id": "msg_prueba", "type": "message", "role": "assistant", "status": "completed",
                "content": [{"type": "output_text", "text": texto, "annotations": []}],
            }]}


def instalar_transporte(monkeypatch, responder):
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    def crear():
        return AsyncOpenAI(api_key="prueba", base_url="https://proveedor.test/v1",
                           http_client=httpx.AsyncClient(transport=httpx.MockTransport(responder)))
    monkeypatch.setattr(llm, "crear_cliente", crear)


def test_clasificacion_usa_responses_y_esquema(monkeypatch):
    def proveedor(request):
        assert request.url.path == "/v1/responses"
        cuerpo = json.loads(request.content)
        assert cuerpo["input"][1]["content"] == "Llegó otro producto"
        assert cuerpo["text"]["format"]["type"] == "json_schema"
        assert cuerpo["store"] is False
        assert "messages" not in cuerpo and "response_format" not in cuerpo
        texto = json.dumps({"intencion": "devolucion", "sentimiento": "negativo",
                            "urgencia": "media", "evidencia": "otro producto"})
        return httpx.Response(200, json=respuesta_http(texto))
    instalar_transporte(monkeypatch, proveedor)
    assert asyncio.run(llm.clasificar("Llegó otro producto")).intencion == "devolucion"


@pytest.mark.parametrize("texto,status", [("", "completed"), ("{}", "completed"), ("{}", "incomplete")])
def test_rechaza_salida_vacia_invalida_o_incompleta(monkeypatch, texto, status):
    instalar_transporte(monkeypatch, lambda _: httpx.Response(200, json=respuesta_http(texto, status=status)))
    with pytest.raises(RuntimeError):
        asyncio.run(llm.clasificar("hola"))
