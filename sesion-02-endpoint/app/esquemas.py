"""Los contratos del servicio. Se escriben antes que el código, porque son lo
único que otra persona necesita leer para consumirlo."""

from typing import Literal

from pydantic import BaseModel, Field

Area = Literal["facturacion", "tecnico", "comercial", "otros"]
Urgencia = Literal["baja", "media", "alta"]


class Entrada(BaseModel):
    id: str
    texto: str = Field(min_length=1, max_length=8000,
                       description="El texto del reclamo.")
    canal: Literal["correo", "chat", "formulario"]


class Salida(BaseModel):
    area: Area
    urgencia: Urgencia
    confianza: float = Field(ge=0, le=1)
    evidencia: str = Field(
        default="",
        description="La frase del mensaje en la que se apoya la decisión. "
        "Cuando alguien discuta una etiqueta, esto cierra la discusión.",
    )
