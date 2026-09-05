"""Los contratos del servicio. Escríbalos antes de tocar el endpoint."""

from typing import Literal

from pydantic import BaseModel, Field


# TODO: defina Entrada con id, texto y canal.
#       texto acepta entre 1 y 8000 caracteres.
#       canal solo acepta correo, chat o formulario.


# TODO: defina Salida con area, urgencia, confianza y evidencia.
#       Use Literal para las listas cerradas y Field para el rango de confianza.
