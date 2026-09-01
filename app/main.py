"""El servicio. Sesión 2 lo levanta, la 6 lo instrumenta y lo despliega."""

import json
import os

from fastapi import Depends, FastAPI, Header, HTTPException
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from pydantic import ValidationError

from app import trazas
from app.chat import router as router_chat
from app.esquemas import Entrada, Salida
from app.modelo import triar

trazas.iniciar()

app = FastAPI(title="Triaje de reclamos", version="1.0.0")

# Instrumentación automática: cada petición HTTP ya queda como span padre.
# Los tramos de adentro cuelgan solos de él.
FastAPIInstrumentor.instrument_app(app)


def clave(x_api_key: str | None = Header(default=None)):
    """FastAPI mapea x_api_key a la cabecera X-API-Key sin que haya que decirlo.

    El default=None importa: sin él la cabecera es obligatoria y FastAPI
    responde 422 cuando falta, que es un error de validación. Faltar la
    credencial no es un problema de forma, así que corresponde 401.
    """
    if x_api_key != os.environ["API_KEY"]:
        raise HTTPException(401, "clave inválida")


@app.get("/salud")
def salud():
    return {"estado": "ok"}


# La conversación de la sesión 3 vive en su propio archivo y se monta acá,
# detrás de la misma clave.
app.include_router(router_chat, dependencies=[Depends(clave)])


@app.post("/reclamos", response_model=Salida, dependencies=[Depends(clave)])
def clasificar(e: Entrada) -> Salida:
    for _ in range(2):
        try:
            with trazas.span("validar_salida"):
                return Salida.model_validate(triar(e.texto))
        except (json.JSONDecodeError, ValidationError):
            continue
    raise HTTPException(422, "salida no válida")
