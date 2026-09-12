"""Contratos HTTP y de las herramientas."""

from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator


TextoBreve = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=800)]
Motivo = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=800,
                                           pattern=r"^[^\r\n]+$")]
PedidoId = Annotated[str, StringConstraints(pattern=r"^P-[0-9]{4}$")]


class Clasificacion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    intencion: Literal["estado_pedido", "devolucion", "otro"]
    sentimiento: Literal["positivo", "neutral", "negativo"]
    urgencia: Literal["baja", "media", "alta"]
    evidencia: TextoBreve


class SolicitudClasificacion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mensaje: TextoBreve


class Turno(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rol: Literal["usuario", "asistente"]
    contenido: TextoBreve


class Confirmacion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    acepta: Literal[True]
    pedido_id: PedidoId
    motivo: Motivo
    propuesta_token: Annotated[str, StringConstraints(min_length=20, max_length=1200)]


class Propuesta(BaseModel):
    pedido_id: PedidoId
    motivo: Motivo
    propuesta_token: str
    accion: Literal["registrar_solicitud_para_revision"] = "registrar_solicitud_para_revision"


class SolicitudChat(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mensaje: TextoBreve
    pedido_id: PedidoId | None = None
    motivo: Motivo | None = None
    historial: list[Turno] = Field(default_factory=list, max_length=12)
    confirmacion: Confirmacion | None = None

    @model_validator(mode="after")
    def validar_confirmacion(self):
        if self.confirmacion and (
            self.pedido_id != self.confirmacion.pedido_id
            or self.motivo != self.confirmacion.motivo
        ):
            raise ValueError("La confirmación debe coincidir con pedido_id y motivo.")
        return self


class Pedido(BaseModel):
    pedido_id: PedidoId
    cliente_id: str
    fecha: date
    fecha_entrega: date | None
    estado: str
    producto: str
    entregado: bool


class Politica(BaseModel):
    tipo: Literal["devolucion"]
    dias: int
    condiciones: str


SolicitudId = Annotated[str, StringConstraints(pattern=r"^SOL-[A-F0-9]{12}$")]


class SolicitudRegistrada(BaseModel):
    solicitud_id: SolicitudId
    pedido_id: PedidoId
    cliente_id: str
    motivo: Motivo
    estado: Literal["recibida_para_revision"]
    nota: str


class RegistroHerramienta(BaseModel):
    nombre: Literal["consultar_pedido", "consultar_politica", "registrar_solicitud"]
    argumentos: dict
    resultado: dict
    origen: Literal["modelo", "aplicacion"]


class RespuestaChat(BaseModel):
    respuesta: str
    herramientas: list[RegistroHerramienta]
    propuesta: Propuesta | None = None
    solicitud_id: SolicitudId | None = None
