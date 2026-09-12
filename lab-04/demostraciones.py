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


def lote_abc():
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from servicio import crm, lote
    from servicio.contratos import Clasificacion
    mensajes = {'A': '¿Dónde está P-1042?', 'B': 'Recibí un producto distinto.', 'C': 'Gracias por resolver mi consulta.'}
    claves = {v: k for k, v in mensajes.items()}
    llamadas = []

    async def clasificar_controlado(mensaje):
        letra = claves[mensaje]
        llamadas.append(letra)
        if letra == 'B' and llamadas.count('B') == 1:
            raise RuntimeError('Fallo didáctico de B, solo la primera vez')
        return Clasificacion(
            intencion={'A': 'estado_pedido', 'B': 'devolucion', 'C': 'otro'}[letra],
            sentimiento={'A': 'neutral', 'B': 'negativo', 'C': 'positivo'}[letra],
            urgencia='media', evidencia=mensaje,
        )

    with tempfile.TemporaryDirectory(prefix='bsg-demo-abc-') as carpeta:
        base = Path(carpeta)
        entrada = base / 'mensajes'
        entrada.mkdir()
        for nombre, mensaje in mensajes.items():
            (entrada / f'{nombre}.txt').write_text(mensaje, encoding='utf-8')
        # All writes are temporary, even if the local .env configures a bucket.
        with patch.dict(os.environ, {'CRM_BUCKET': '', 'LANGFUSE_ENABLED': 'false'}), patch.object(crm, 'CARPETA_CRM', base / 'crm'), patch.object(lote, 'clasificar', clasificar_controlado):
            primera = asyncio.run(lote.procesar_carpeta(entrada))
            print('PRIMERA EJECUCIÓN DEL BUCLE REAL CON CLASIFICADOR CONTROLADO')
            print(primera.model_dump_json(indent=2))
            print('Llamadas:', ', '.join(llamadas))
            assert primera.procesados == 2 and primera.omitidos == 0 and 'B.txt' in primera.errores
            assert len(list((base / 'crm/analisis').glob('ANA-*.txt'))) == 2
            segunda = asyncio.run(lote.procesar_carpeta(entrada))
            print('\nSEGUNDA EJECUCIÓN')
            print(segunda.model_dump_json(indent=2))
            print('Llamadas acumuladas:', ', '.join(llamadas))
            assert segunda.procesados == 1 and segunda.omitidos == 2 and not segunda.errores
            assert llamadas == ['A', 'B', 'C', 'B']
            assert len(list((base / 'crm/analisis').glob('ANA-*.txt'))) == 3
            print('Tres ANA en carpeta temporal. No se modificó el CRM del curso.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ejemplo', choices=['await', 'lote'])
    args = parser.parse_args()
    if args.ejemplo == 'await': asyncio.run(espera())
    else: lote_abc()
