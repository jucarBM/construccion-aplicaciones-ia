"""Lectura del CRM TXT y creación exclusiva de archivos de este laboratorio."""

import hashlib
from pathlib import Path

from .configuracion import RAIZ, fecha_escenario
from .contratos import Pedido, Politica, SolicitudRegistrada


CARPETA_CRM = RAIZ / "crm"


def _filas(nombre: str):
    lineas = (CARPETA_CRM / nombre).read_text(encoding="utf-8").splitlines()
    encabezados = [campo.strip() for campo in lineas[0].split("|")]
    for linea in lineas[1:]:
        if linea.strip() and not linea.lstrip().startswith("#"):
            yield dict(zip(encabezados, (valor.strip() for valor in linea.split("|"))))


def consultar_pedido(pedido_id: str, cliente_id: str) -> Pedido | None:
    for fila in _filas("pedidos.txt"):
        if fila["pedido_id"] == pedido_id and fila["cliente_id"] == cliente_id:
            datos = {**fila, "fecha_entrega": fila.get("fecha_entrega") or None,
                     "entregado": fila["entregado"].lower() == "si"}
            return Pedido.model_validate(datos)
    return None


def consultar_politica(tipo: str) -> Politica | None:
    for fila in _filas("politicas.txt"):
        if fila["tipo"] == tipo:
            return Politica(tipo=tipo, dias=int(fila["dias"]), condiciones=fila["condiciones"])
    return None


def _id(prefijo: str, clave: str) -> str:
    return f"{prefijo}-{hashlib.sha256(clave.encode()).hexdigest()[:12].upper()}"


def registrar_solicitud(pedido: Pedido, motivo: str) -> tuple[str, bool]:
    solicitud_id = _id("SOL", f"{pedido.cliente_id}|{pedido.pedido_id}|{motivo}")
    contenido = (
        f"solicitud_id: {solicitud_id}\n"
        f"pedido_id: {pedido.pedido_id}\n"
        f"cliente_id: {pedido.cliente_id}\n"
        f"motivo: {motivo}\n"
        "estado: recibida_para_revision\n"
        "nota: Registrar no aprueba la devolución ni ejecuta un reembolso.\n"
    )
    creada = _crear(f"solicitudes/{solicitud_id}.txt", contenido)
    return solicitud_id, creada


def evaluar_devolucion(pedido: Pedido, politica: Politica) -> tuple[bool | None, str]:
    if not pedido.entregado:
        return False, "El pedido aún no fue entregado."
    if not pedido.fecha_entrega:
        return None, "Falta la fecha de entrega; se requiere revisión humana."
    dias = (fecha_escenario() - pedido.fecha_entrega).days
    if dias < 0:
        return None, "La fecha de entrega es inconsistente; se requiere revisión humana."
    if dias > politica.dias:
        return False, f"Han pasado {dias} días y la política indica {politica.dias}."
    return True, f"Han pasado {dias} días desde la entrega; el plazo es {politica.dias}."


def _crear(nombre: str, contenido: str) -> bool:
    destino = CARPETA_CRM / nombre
    destino.parent.mkdir(parents=True, exist_ok=True)
    try:
        with destino.open("x", encoding="utf-8") as archivo:
            archivo.write(contenido)
        return True
    except FileExistsError:
        return False

def leer_solicitud(solicitud_id: str, cliente_id: str) -> SolicitudRegistrada | None:
    ruta = CARPETA_CRM / f"solicitudes/{solicitud_id}.txt"
    if not ruta.is_file():
        return None
    texto = ruta.read_text(encoding="utf-8")
    datos = dict(linea.split(": ", 1) for linea in texto.splitlines() if ": " in linea)
    if datos.get("cliente_id") != cliente_id:
        return None
    return SolicitudRegistrada.model_validate(datos)
