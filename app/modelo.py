"""La llamada al proveedor, separada del servidor HTTP."""

import json
import os

from openai import OpenAI

from app import exigir


MODELO = os.getenv("MODELO", "openai/gpt-4o-mini")

# TODO: cree el cliente con base_url de OpenRouter y OPENROUTER_API_KEY.


SISTEMA = """Clasificas reclamos de una empresa de servicios.

Devuelves únicamente un objeto JSON con area, urgencia, confianza y evidencia.
No explicas ni agregas claves. Si el mensaje no alcanza para decidir, usa area
otros y confianza baja."""


def triar(texto: str) -> dict:
    """TODO: llame al modelo, pida JSON y devuelva json.loads de su respuesta."""
    raise NotImplementedError
