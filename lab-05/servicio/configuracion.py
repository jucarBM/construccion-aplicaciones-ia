"""Configuración, autenticación sencilla y observabilidad opcional."""

import os
import secrets
from datetime import date
from contextlib import contextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Header, HTTPException


RAIZ = Path(__file__).resolve().parents[1]
load_dotenv(RAIZ / ".env")


def api_key_esperada() -> str:
    clave = os.getenv("API_KEY")
    if clave:
        return clave
    if os.getenv("K_SERVICE"):
        raise RuntimeError("API_KEY es obligatoria en Cloud Run.")
    return "curso-local"


def exigir_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if not x_api_key or not secrets.compare_digest(x_api_key, api_key_esperada()):
        raise HTTPException(status_code=401, detail="Credencial inválida.")


def cliente_demo() -> str:
    return os.getenv("CLIENTE_DEMO", "C-001")


def fecha_escenario() -> date:
    return date.fromisoformat(os.getenv("FECHA_ESCENARIO", "2026-09-08"))


def validar_configuracion_servicio() -> None:
    if os.getenv("K_SERVICE"):
        if not os.getenv("API_KEY") or not os.getenv("PROPUESTA_SECRET"):
            raise RuntimeError("API_KEY y PROPUESTA_SECRET son obligatorias en Cloud Run.")


def trazas_activas() -> bool:
    return os.getenv("LANGFUSE_ENABLED", "false").lower() == "true"


@contextmanager
def observacion(nombre: str, entrada=None):
    if not trazas_activas():
        yield None
        return
    requeridas = ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_BASE_URL")
    if not all(os.getenv(variable) for variable in requeridas):
        raise RuntimeError("Completa las variables de Langfuse o desactiva LANGFUSE_ENABLED.")
    from langfuse import get_client

    cliente = get_client()
    from opentelemetry.trace import get_current_span

    es_raiz = not get_current_span().get_span_context().is_valid
    try:
        with cliente.start_as_current_observation(name=nombre, input=entrada) as tramo:
            yield tramo
    finally:
        if es_raiz:
            cliente.flush()  # Cloud Run puede pausar la CPU después de responder.


def trace_id() -> str | None:
    if not trazas_activas():
        return None
    from langfuse import get_client

    return get_client().get_current_trace_id()
