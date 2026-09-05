"""El contraste con sus sistemas.

Es la casilla 6 de la ficha: «¿existe la factura y es del titular? Si no, va a
revisión humana». Sin esta capa no hay caso, hay demo — el modelo puede
clasificar perfecto un reclamo sobre una factura que no existe.

Acá el ERP es un archivo, para que el laboratorio corra sin conectarse a nada.
En la empresa se cambia esta función por la llamada de verdad y no se toca
nada más: por eso vive aparte del endpoint.
"""

import json
import pathlib
import re

ERP = pathlib.Path(__file__).resolve().parent.parent / "datos" / "facturas.jsonl"

# Las facturas del caso se escriben 88-4412. Se busca en el texto del cliente
# porque es donde viene: nadie completa un formulario con el número aparte.
NUMERO = re.compile(r"\b\d{2}-\d{4}\b")


def _facturas() -> dict[str, dict]:
    if not ERP.exists():
        return {}
    return {
        f["numero"]: f
        for f in (json.loads(l) for l in ERP.read_text(encoding="utf8").splitlines() if l.strip())
    }


def cuadra(texto: str) -> str | None:
    """Devuelve el motivo por el que no cuadra, o None si está todo bien.

    Un texto que no menciona ninguna factura cuadra: no hay nada que contrastar.
    El 409 es para cuando el cliente afirma algo que el sistema desmiente, que
    es distinto de que el modelo se haya equivocado.
    """
    citado = NUMERO.search(texto)
    if not citado:
        return None
    numero = citado.group()
    factura = _facturas().get(numero)
    if factura is None:
        return f"la factura {numero} no existe"
    if factura.get("anulada"):
        return f"la factura {numero} está anulada"
    return None
