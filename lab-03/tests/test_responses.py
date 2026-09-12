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

def test_consulta_conserva_items_y_devuelve_resultado(cliente, headers, monkeypatch):
    peticiones = []
    razonamiento = {"id": "rs_1", "type": "reasoning", "summary": [], "encrypted_content": "contexto_opaco"}
    llamada = {"id": "fc_1", "type": "function_call", "call_id": "consulta_1",
               "name": "consultar_pedido", "arguments": '{"pedido_id":"P-1042"}', "status": "completed"}
    def proveedor(request):
        assert request.url.path == "/v1/responses"
        cuerpo = json.loads(request.content)
        peticiones.append(cuerpo)
        assert cuerpo["tools"][0]["name"] == "consultar_pedido"
        assert "function" not in cuerpo["tools"][0]
        if len(peticiones) == 1:
            return httpx.Response(200, json=respuesta_http("", [razonamiento, llamada]))
        entrada = cuerpo["input"]
        assert razonamiento in entrada and llamada in entrada
        resultado = entrada[-1]
        assert resultado["type"] == "function_call_output"
        assert resultado["call_id"] == "consulta_1"
        assert json.loads(resultado["output"])["producto"] == "Audífonos negros"
        return httpx.Response(200, json=respuesta_http("El pedido registra Audífonos negros."))
    instalar_transporte(monkeypatch, proveedor)
    respuesta = cliente.post("/api/chat", headers=headers, json={
        "mensaje": "¿Qué producto figura en P-1042?", "pedido_id": "P-1042",
    })
    assert respuesta.status_code == 200
    assert len(peticiones) == 2
    assert respuesta.json()["herramientas"][0]["resultado"]["pedido_id"] == "P-1042"
    assert respuesta.json()["solicitud_id"] is None


def test_historial_es_explicito_y_acotado():
    from servicio.chat import preparar_mensajes
    from servicio.contratos import SolicitudChat
    entrada = SolicitudChat(mensaje="¿Cuándo?", historial=[
        {"rol": "usuario" if i % 2 == 0 else "asistente", "contenido": f"Mensaje {i}"}
        for i in range(12)
    ])
    mensajes = preparar_mensajes(entrada)
    assert len(mensajes) == 10
    assert mensajes[1] == {"role": "user", "content": "Mensaje 4"}
    assert mensajes[-2] == {"role": "assistant", "content": "Mensaje 11"}
    assert json.loads(mensajes[-1]["content"])["mensaje"] == "¿Cuándo?"
