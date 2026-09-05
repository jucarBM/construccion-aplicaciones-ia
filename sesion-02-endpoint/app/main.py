"""El servicio. Sesión 2 lo levanta, la 6 lo instrumenta y lo despliega."""

import json

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import ValidationError

from app import exigir
from app.esquemas import Entrada, Salida
from app.modelo import triar

app = FastAPI(title="Triaje de reclamos", version="1.0.0")


def clave(x_api_key: str | None = Header(default=None)):
    """FastAPI mapea x_api_key a la cabecera X-API-Key sin que haya que decirlo.

    El default=None importa: sin él la cabecera es obligatoria y FastAPI
    responde 422 cuando falta, que es un error de validación. Faltar la
    credencial no es un problema de forma, así que corresponde 401.
    """
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
