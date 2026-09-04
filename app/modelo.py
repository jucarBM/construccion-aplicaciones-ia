"""La llamada al proveedor, en su propio archivo.

Vive aparte del servidor por una razón práctica: así se puede probar desde una
terminal, sin levantar la API. Es la lámina 8 de la sesión 2, entera.
"""

import json
import os

from openai import OpenAI

from app import exigir
from app.trazas import span_modelo

MODELO = os.getenv("MODELO", "openai/gpt-4o-mini")

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
    with span_modelo(MODELO) as span:
        r = cliente.chat.completions.create(
            model=MODELO,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SISTEMA},
                {"role": "user", "content": texto},
            ],
        )
        span.anotar_uso(r)
        return json.loads(r.choices[0].message.content)
