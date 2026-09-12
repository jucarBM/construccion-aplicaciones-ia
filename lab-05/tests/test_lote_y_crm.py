import asyncio
from pathlib import Path

from servicio import lote
from servicio.contratos import Clasificacion


def test_lote_es_reanudable_y_no_duplica(crm_aislado, tmp_path: Path, monkeypatch):
    entrada = tmp_path / "mensajes"
    entrada.mkdir()
    entrada.joinpath("uno.txt").write_text("Producto distinto", encoding="utf-8")

    llamadas = []

    async def clasificar_falso(mensaje):
        llamadas.append(mensaje)
        return Clasificacion(intencion="devolucion", sentimiento="negativo",
                             urgencia="media", evidencia="Producto distinto")

    monkeypatch.setattr(lote, "clasificar", clasificar_falso)
    primera = asyncio.run(lote.procesar_carpeta(entrada))
    segunda = asyncio.run(lote.procesar_carpeta(entrada))
    assert primera.model_dump(exclude={"errores"}) == {
        "encontrados": 1, "procesados": 1, "omitidos": 0,
    }
    assert segunda.model_dump(exclude={"errores"}) == {
        "encontrados": 1, "procesados": 0, "omitidos": 1,
    }
    assert len(list((crm_aislado / "analisis").glob("ANA-*.txt"))) == 1
    assert llamadas == ["Producto distinto"]


def test_lote_aisla_error_y_deja_reintento(crm_aislado, tmp_path: Path, monkeypatch):
    entrada = tmp_path / "mensajes"
    entrada.mkdir()
    entrada.joinpath("vacio.txt").write_text("", encoding="utf-8")

    async def no_debe_llamarse(_):
        raise AssertionError

    monkeypatch.setattr(lote, "clasificar", no_debe_llamarse)
    resultado = asyncio.run(lote.procesar_carpeta(entrada))
    assert resultado.procesados == 0
    assert resultado.errores == {"vacio.txt": "mensaje vacío"}
    assert not (crm_aislado / "analisis").exists()


def test_reanudar_llama_solo_al_archivo_pendiente(crm_aislado, tmp_path, monkeypatch):
    entrada = tmp_path / "mensajes"
    entrada.mkdir()
    for nombre in ("a", "b"):
        (entrada / f"{nombre}.txt").write_text(nombre)
    llamadas = []

    async def clasificar_controlado(mensaje):
        llamadas.append(mensaje)
        if mensaje == "b" and llamadas.count("b") == 1:
            raise RuntimeError("Proveedor temporalmente no disponible")
        return Clasificacion(intencion="otro", sentimiento="neutral",
                             urgencia="baja", evidencia=mensaje)

    monkeypatch.setattr(lote, "clasificar", clasificar_controlado)
    primera = asyncio.run(lote.procesar_carpeta(entrada))
    segunda = asyncio.run(lote.procesar_carpeta(entrada))
    assert primera.procesados == 1 and "b.txt" in primera.errores
    assert segunda.procesados == 1 and segunda.omitidos == 1
    assert segunda.errores == {}
    assert llamadas == ["a", "b", "b"]
