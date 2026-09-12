"""Ejemplos docentes controlados. No llaman a modelos ni a GCP."""
import argparse
import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch


async def espera():
    eventos = []
    async def peticion_a():
        eventos.append('A envía una petición al proveedor simulado')
        eventos.append('A espera con await')
        await asyncio.sleep(0.3)
        eventos.append('A recibe el resultado y termina')
    async def peticion_b():
        await asyncio.sleep(0.1)
        eventos.append('B comienza durante la espera de A')
        eventos.append('B termina mientras A todavía espera')
    await asyncio.gather(peticion_a(), peticion_b())
    print('CRONOLOGÍA SIMULADA: ilustra async, no mide FastAPI ni un modelo real.')
    for i, e in enumerate(eventos, 1): print(f'{i}. {e}')
    assert eventos.index('B termina mientras A todavía espera') < eventos.index('A recibe el resultado y termina')




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ejemplo', choices=['await'])
    args = parser.parse_args()
    if args.ejemplo == 'await': asyncio.run(espera())
