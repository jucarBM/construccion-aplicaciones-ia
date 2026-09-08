"""Definición y ejecución controlada de las tres herramientas del asistente."""

from pydantic import BaseModel, ConfigDict, ValidationError

from .configuracion import cliente_demo
from .contratos import PedidoId, RegistroHerramienta, SolicitudChat
from .crm import (consultar_pedido, consultar_politica, evaluar_devolucion,
                  registrar_solicitud)
from .seguridad import propuesta_valida


class ArgsPedido(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pedido_id: PedidoId


class ArgsPolitica(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tipo: str


class ArgsRegistro(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pedido_id: PedidoId
    motivo: str


def _herramienta(nombre: str, descripcion: str, esquema: dict) -> dict:
    return {"type": "function", "function": {"name": nombre, "description": descripcion,
            "strict": True, "parameters": esquema}}


HERRAMIENTAS = [
    _herramienta("consultar_pedido", "Consulta el pedido indicado del cliente autenticado.", ArgsPedido.model_json_schema()),
    _herramienta("consultar_politica", "Consulta la política de devolución.", ArgsPolitica.model_json_schema()),
    _herramienta("registrar_solicitud", "Registra una solicitud solo si el cliente ya confirmó en el cuerpo HTTP.", ArgsRegistro.model_json_schema()),
]


def ejecutar(nombre: str, argumentos: dict, entrada: SolicitudChat, origen="modelo") -> RegistroHerramienta:
    try:
        if nombre == "consultar_pedido":
            args = ArgsPedido.model_validate(argumentos)
            pedido = consultar_pedido(args.pedido_id, cliente_demo())
            resultado = pedido.model_dump(mode="json") if pedido else {"error": "pedido_no_encontrado"}
        elif nombre == "consultar_politica":
            args = ArgsPolitica.model_validate(argumentos)
            if args.tipo != "devolucion":
                resultado = {"error": "politica_no_disponible"}
            else:
                politica = consultar_politica(args.tipo)
                resultado = politica.model_dump(mode="json") if politica else {"error": "politica_no_disponible"}
        elif nombre == "registrar_solicitud":
            args = ArgsRegistro.model_validate(argumentos)
            if not entrada.confirmacion or (
                args.pedido_id != entrada.confirmacion.pedido_id
                or args.motivo != entrada.confirmacion.motivo
                or not propuesta_valida(
                    entrada.confirmacion.propuesta_token,
                    cliente_demo(),
                    args.pedido_id,
                    args.motivo,
                )
            ):
                resultado = {"error": "confirmacion_http_valida_requerida"}
            else:
                pedido = consultar_pedido(args.pedido_id, cliente_demo())
                if not pedido:
                    resultado = {"error": "pedido_no_encontrado"}
                else:
                    politica = consultar_politica("devolucion")
                    elegible, explicacion = (
                        evaluar_devolucion(pedido, politica)
                        if politica else (None, "Falta la política de devolución.")
                    )
                    if elegible is not True:
                        resultado = {"error": "revision_humana_requerida",
                                     "explicacion": explicacion}
                    else:
                        solicitud_id, creada = registrar_solicitud(pedido, args.motivo)
                        resultado = {"solicitud_id": solicitud_id, "creada": creada,
                                     "estado": "recibida_para_revision"}
        else:
            resultado = {"error": "herramienta_no_permitida"}
    except ValidationError:
        resultado = {"error": "argumentos_invalidos"}
    return RegistroHerramienta(nombre=nombre, argumentos=argumentos, resultado=resultado, origen=origen)
