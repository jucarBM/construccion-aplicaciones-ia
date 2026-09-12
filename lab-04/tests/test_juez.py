import importlib.util
import json
from pathlib import Path

import httpx
from openai import OpenAI
from pydantic import BaseModel


def test_juez_usa_responses_con_schema_y_texto(monkeypatch):
    archivo = Path(__file__).resolve().parents[1] / "evaluacion/evaluar.py"
    spec = importlib.util.spec_from_file_location("evaluador_local", archivo)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    llamadas = []
    def proveedor(request):
        cuerpo = json.loads(request.content)
        llamadas.append(cuerpo)
        assert request.url.path == "/v1/responses"
        assert cuerpo["store"] is False
        texto = '{"aprobado":true}' if "text" in cuerpo else "Explicación"
        return httpx.Response(200, json={
            "id": "resp_test", "object": "response", "created_at": 0, "model": "gpt-4o-mini",
            "status": "completed", "parallel_tool_calls": False, "tool_choice": "auto", "tools": [],
            "output": [{"type": "message", "id": "msg_test", "role": "assistant", "status": "completed",
                        "content": [{"type": "output_text", "text": texto, "annotations": []}]}],
        })
    monkeypatch.setenv("OPENAI_API_KEY", "prueba")
    monkeypatch.setattr(modulo, "OpenAI", lambda **kwargs: OpenAI(
        api_key="prueba", base_url="https://proveedor.test/v1",
        http_client=httpx.Client(transport=httpx.MockTransport(proveedor)),
    ))
    class Veredicto(BaseModel):
        aprobado: bool
    juez = modulo.JuezResponses(model="gpt-4o-mini")
    assert juez.generate("Evalúa", Veredicto).aprobado is True
    assert juez.generate("Explica") == "Explicación"
    assert len(llamadas) == 2
