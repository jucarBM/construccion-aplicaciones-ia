"""Contratos de la API de clasificación."""
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, StringConstraints

TextoBreve = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=800)]

class Clasificacion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    intencion: Literal["estado_pedido", "devolucion", "otro"]
    sentimiento: Literal["positivo", "neutral", "negativo"]
    urgencia: Literal["baja", "media", "alta"]
    evidencia: TextoBreve

class SolicitudClasificacion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mensaje: TextoBreve
