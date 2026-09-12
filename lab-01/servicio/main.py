"""Aplicación completa de lab-01, ejecutable de forma independiente."""


from fastapi import Depends, FastAPI, HTTPException

from .configuracion import exigir_api_key
from .contratos import Clasificacion, SolicitudClasificacion
from .llm import clasificar




app = FastAPI(title="Tienda IA · lab-01", version="1.0.0")
protegida = [Depends(exigir_api_key)]


@app.get("/salud")
def salud():
    return {"estado": "ok"}


@app.post("/api/clasificar", response_model=Clasificacion, dependencies=protegida)
async def clasificar_mensaje(entrada: SolicitudClasificacion):
    try:
        resultado = await clasificar(entrada.mensaje)
        return resultado
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
