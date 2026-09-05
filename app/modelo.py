"""La llamada al proveedor, separada del servidor HTTP."""

import json
import os

from openai import OpenAI

from app import exigir


MODELO = os.getenv("MODELO", "openai/gpt-4o-mini")
DEMO_MODE = os.getenv("DEMO_MODE") == "1"

if DEMO_MODE:
    cliente = None
else:
    cliente = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=exigir("OPENROUTER_API_KEY", "la clave del proveedor de modelos"),
    )

SISTEMA = """Clasificas reclamos de una empresa de servicios.

Devuelves únicamente un objeto JSON con estas cuatro claves:
  area        facturacion | tecnico | comercial | otros
  urgencia    baja | media | alta
  confianza   número entre 0 y 1
  evidencia   la frase textual del mensaje en la que te apoyas

No explicas. No agregas claves. Si el mensaje no alcanza para decidir,
devuelves area "otros" con confianza baja."""


def triar(texto: str) -> dict:
    """Devuelve el diccionario crudo del modelo. Quien llama lo valida."""
    if DEMO_MODE:
        return {
            "area": "otros",
            "urgencia": "media",
            "confianza": 0.5,
            "evidencia": "modo de demostración: respuesta fija",
        }

    respuesta = cliente.chat.completions.create(
        model=MODELO,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SISTEMA},
            {"role": "user", "content": texto},
        ],
    )
    return json.loads(respuesta.choices[0].message.content)
