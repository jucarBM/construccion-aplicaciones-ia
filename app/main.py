"""El servicio HTTP de la sesión 2."""

import json

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import ValidationError

from app import exigir
from app.esquemas import Entrada, Salida
from app.modelo import triar


app = FastAPI(title="Triaje de reclamos", version="1.0.0")


def clave(x_api_key: str | None = Header(default=None)):
    """Exige la cabecera X-API-Key antes de gastar tokens."""
    if x_api_key != exigir("API_KEY", "la clave que su servicio le exige a quien lo llama"):
        raise HTTPException(401, "clave inválida")


@app.get("/salud")
def salud():
    return {"estado": "ok"}


@app.post("/reclamos", response_model=Salida, dependencies=[Depends(clave)])
def clasificar(e: Entrada) -> Salida:
    for _ in range(2):
        try:
            return Salida.model_validate(triar(e.texto))
        except (json.JSONDecodeError, ValidationError):
            continue
    raise HTTPException(422, "salida no válida")
