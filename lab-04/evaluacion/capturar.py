"""Ejecuta los casos contra la API y guarda solo herramientas observadas."""

import argparse
import json
import os
from pathlib import Path
from time import perf_counter

import httpx
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parents[1]
load_dotenv(RAIZ / ".env")


def capturar(url: str, casos: Path, salida: Path):
    salida.parent.mkdir(parents=True, exist_ok=True)
    # El archivo de cada ejecución es nuevo: no sobreescribe evidencia anterior.
    with salida.open("x", encoding="utf-8") as archivo:
        with httpx.Client(base_url=url, headers={"X-API-Key": os.environ["API_KEY"]}, timeout=120) as api:
            for caso in json.loads(casos.read_text(encoding="utf-8")):
                inicio = perf_counter()
                respuesta = api.post("/api/chat", json=caso["entrada"])
                respuesta.raise_for_status()
                real = respuesta.json()
                registro = {
                    "id": caso["id"],
                    "input": json.dumps(caso["entrada"], ensure_ascii=False),
                    "actual_output": real["respuesta"],
                    "expected_output": caso["esperado"],
                    "tools_called": [
                        {"name": x["nombre"], "input_parameters": x["argumentos"], "output": x["resultado"]}
                        for x in real["herramientas"]
                    ],
                    "expected_tools": caso["herramientas_esperadas"],
                    "context": [json.dumps(real["herramientas"], ensure_ascii=False)],
                    "latencia_ms": round((perf_counter() - inicio) * 1000),
                    "trace_id": real.get("trace_id"),
                }
                archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")
                archivo.flush()
                print(f"{caso['id']}: HTTP {respuesta.status_code}; {len(real['herramientas'])} herramientas; {registro['latencia_ms']} ms")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--casos", type=Path, default=RAIZ / "evaluacion/casos.json")
    parser.add_argument("--salida", type=Path, required=True)
    args = parser.parse_args()
    capturar(args.url, args.casos, args.salida)
