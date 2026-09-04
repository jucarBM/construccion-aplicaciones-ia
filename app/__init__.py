"""Carga el .env y comprueba las claves antes de que falle en otro lado.

El README dice `cp .env.example .env` y después `uvicorn app.main:app`. Sin
esto, nada leía ese archivo: la primera corrida moría con

    KeyError: 'OPENROUTER_API_KEY'

en medio de una traza de importaciones, que es el peor mensaje posible para
alguien que está empezando. Ahora el .env se lee solo y, si falta una clave,
lo que se ve es qué falta y dónde ponerlo.

Se importa antes que cualquier submódulo de `app`, así que vale igual para el
servicio, para el lote y para las evaluaciones.
"""

import os
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ENV = RAIZ / ".env"


def _cargar_env() -> None:
    """Lee el .env sin depender de ninguna biblioteca.

    Son doce líneas y evita una dependencia más en la primera clase. Las
    variables que ya estén en el entorno mandan: así el contenedor y Cloud Run,
    que inyectan las suyas, no quedan pisados por un .env olvidado en la imagen.
    """
    if not ENV.exists():
        return
    for linea in ENV.read_text(encoding="utf8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        os.environ.setdefault(clave.strip(), valor.strip().strip("\"'"))


def sin_completar(valor: str | None) -> bool:
    """El .env.example trae `sk-or-v1-...` y `sk-...` de muestra.

    Copiar el ejemplo y olvidarse de completarlo es el tropiezo más común de la
    primera clase, y como el valor no está vacío pasaba el control y reventaba
    después con un AuthenticationError del proveedor, que no dice qué hacer.
    """
    return not valor or valor.endswith("...") or valor.startswith("una-clave-larga")


def exigir(nombre: str, para: str) -> str:
    """Devuelve la variable, o explica qué falta en vez de reventar con KeyError."""
    valor = os.environ.get(nombre)
    if not sin_completar(valor):
        return valor
    estado = "está sin completar" if valor else "falta"
    raise SystemExit(
        f"\n{nombre} {estado} ({para}).\n\n"
        f"  1. cp .env.example .env\n"
        f"  2. abrir {ENV} y poner el valor de {nombre}\n\n"
        f"Si prefiere no usar archivo: export {nombre}=...\n"
    )


_cargar_env()
