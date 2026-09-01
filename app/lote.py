"""El lote de la sesión 4.

Tres cosas que lo separan de un bucle: un tope de llamadas en paralelo, un
estado por mensaje para poder retomar, y la posibilidad de correrlo dos veces
sin duplicar nada.

    python -m app.lote datos/reclamos.jsonl --dry-run
"""

import argparse
import asyncio
import json
import pathlib
import sqlite3

from app.esquemas import Salida
from app.modelo import triar

# El ocho no es mágico: sale del límite del proveedor multiplicado por lo que
# tarda una llamada. Ocho por segundo, un segundo cada una, ocho en vuelo.
MAX_PARALELO = 8

BD = pathlib.Path("estado.sqlite")


def _conexion():
    c = sqlite3.connect(BD)
    c.execute(
        "CREATE TABLE IF NOT EXISTS procesados ("
        "  id TEXT PRIMARY KEY, area TEXT, urgencia TEXT, confianza REAL)"
    )
    return c


def ya_procesado(c, mensaje_id: str) -> bool:
    return c.execute(
        "SELECT 1 FROM procesados WHERE id = ?", (mensaje_id,)
    ).fetchone() is not None


def guardar(c, mensaje_id: str, s: Salida) -> None:
    """Marcar y guardar el resultado en una sola operación.

    Si se separan, un corte entre las dos deja el mensaje marcado sin
    resultado, y ese es el mensaje que nadie vuelve a mirar nunca.
    """
    c.execute(
        "INSERT OR REPLACE INTO procesados VALUES (?, ?, ?, ?)",
        (mensaje_id, s.area, s.urgencia, s.confianza),
    )
    c.commit()


async def procesar(sem: asyncio.Semaphore, m: dict) -> tuple[str, Salida | None]:
    async with sem:
        try:
            return m["id"], Salida.model_validate(await asyncio.to_thread(triar, m["texto"]))
        except Exception as e:  # el lote sigue; el fallo queda registrado
            print(f"  falló {m['id']}: {type(e).__name__}")
            return m["id"], None


async def correr(ruta: pathlib.Path, dry_run: bool) -> None:
    mensajes = [json.loads(l) for l in ruta.read_text(encoding="utf8").splitlines() if l.strip()]
    c = _conexion()
    pendientes = [m for m in mensajes if not ya_procesado(c, m["id"])]
    print(f"{len(mensajes)} mensajes · {len(pendientes)} pendientes")

    sem = asyncio.Semaphore(MAX_PARALELO)
    resultados = await asyncio.gather(*(procesar(sem, m) for m in pendientes))

    ok = 0
    for mensaje_id, salida in resultados:
        if salida is None:
            continue
        ok += 1
        if dry_run:
            print(f"  [seco] {mensaje_id} → {salida.area}/{salida.urgencia}")
        else:
            guardar(c, mensaje_id, salida)
    print(f"{ok} procesados{' (ensayo en seco, no se guardó nada)' if dry_run else ''}")


def main() -> None:
    p = argparse.ArgumentParser(description="Procesa un lote de reclamos.")
    p.add_argument("archivo", type=pathlib.Path)
    p.add_argument("--dry-run", action="store_true", help="dice qué haría, sin guardar")
    a = p.parse_args()
    asyncio.run(correr(a.archivo, a.dry_run))


if __name__ == "__main__":
    main()
