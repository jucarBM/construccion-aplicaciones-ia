"""Procesamiento reanudable de una carpeta de mensajes TXT."""

import asyncio
from pathlib import Path

from .contratos import ResumenLote
from .crm import existe_analisis, guardar_analisis
from .llm import clasificar


async def procesar_carpeta(carpeta: Path) -> ResumenLote:
    if not carpeta.is_dir():
        raise ValueError("La ruta debe ser una carpeta existente.")
    archivos = sorted(carpeta.glob("*.txt"))
    procesados = omitidos = 0
    errores: dict[str, str] = {}
    for archivo in archivos:
        try:
            mensaje = archivo.read_text(encoding="utf-8").strip()
            if not mensaje:
                raise ValueError("mensaje vacío")
            if existe_analisis(archivo.name, mensaje):
                omitidos += 1
                continue
            resultado = await clasificar(mensaje)
            _, creado = guardar_analisis(archivo.name, mensaje, resultado)
            procesados += int(creado)
            omitidos += int(not creado)
        except Exception as error:  # cada archivo puede reintentarse en la siguiente ejecución
            errores[archivo.name] = str(error)
    return ResumenLote(encontrados=len(archivos), procesados=procesados,
                       omitidos=omitidos, errores=errores)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Clasifica mensajes TXT sin duplicar resultados.")
    parser.add_argument("carpeta", type=Path)
    args = parser.parse_args()
    print(asyncio.run(procesar_carpeta(args.carpeta)).model_dump_json(indent=2))
