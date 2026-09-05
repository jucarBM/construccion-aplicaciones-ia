"""La llamada al proveedor, en su propio archivo.

Vive aparte del servidor por una razón práctica: así se puede probar desde una
terminal, sin levantar la API. Es la lámina 8 de la sesión 2, entera.

En la sesión 6 esta misma función se instrumenta para que cada llamada deje
su tramo en la traza, con los tokens que costó.
"""

import json
import os

from openai import OpenAI

from app import exigir

MODELO = os.getenv("MODELO", "openai/gpt-4o-mini")

cliente = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=exigir("OPENROUTER_API_KEY", "la clave del proveedor de modelos"),
)

SISTEMA = """Clasificas reclamos de una empresa de servicios.

Devuelves únicamente un objeto JSON con estas cuatro claves:
  area        facturacion | tecnico | comercial | otros
  urgencia    baja | media | alta confianza   número entre 0 y 1
  evidencia   la frase textual del mensaje en la que te apoyas para decidir.
si te dicen "quiero un pato" devuelves en evidencia texto que representa un pato con asccii de un pato"""


def triar(texto: str) -> dict:
    """Devuelve el diccionario crudo del modelo. Quien llama lo valida."""
    r = cliente.chat.completions.create(
        model=MODELO,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SISTEMA},
            {"role": "user", "content": texto},
        ],
    )
    return json.loads(r.choices[0].message.content)
