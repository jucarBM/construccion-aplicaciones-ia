"""API única y acumulativa para los cinco laboratorios."""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException

from .chat import conversar
from .configuracion import (cliente_demo, exigir_api_key, observacion,
                            validar_configuracion_servicio)
from .contratos import (Clasificacion, Pedido, Politica, RespuestaChat,
                        SolicitudChat, SolicitudClasificacion, PedidoId,
                        SolicitudId, SolicitudRegistrada)
from .crm import consultar_pedido, consultar_politica, leer_solicitud
from .llm import clasificar


@asynccontextmanager
async def vida(_app: FastAPI):
    validar_configuracion_servicio()
    yield


app = FastAPI(title="Tienda IA", version="1.0.0", lifespan=vida)
protegida = [Depends(exigir_api_key)]


@app.get("/salud")
def salud():
    return {"estado": "ok"}


@app.post("/api/clasificar", response_model=Clasificacion, dependencies=protegida)
async def clasificar_mensaje(entrada: SolicitudClasificacion):
    try:
        with observacion("Clasificar mensaje", entrada.model_dump()) as span:
            resultado = await clasificar(entrada.mensaje)
            if span:
                span.update(output=resultado.model_dump())
            return resultado
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@app.get("/api/pedidos/{pedido_id}", response_model=Pedido, dependencies=protegida)
def obtener_pedido(pedido_id: PedidoId):
    pedido = consultar_pedido(pedido_id, cliente_demo())
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado.")
    return pedido


@app.get("/api/politicas/{tipo}", response_model=Politica, dependencies=protegida)
def obtener_politica(tipo: str):
    politica = consultar_politica(tipo)
    if not politica:
        raise HTTPException(status_code=404, detail="Política no encontrada.")
    return politica


@app.get("/api/solicitudes/{solicitud_id}", response_model=SolicitudRegistrada,
         dependencies=protegida)
def obtener_solicitud(solicitud_id: SolicitudId):
    solicitud = leer_solicitud(solicitud_id, cliente_demo())
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada.")
    return solicitud


@app.post("/api/chat", response_model=RespuestaChat, dependencies=protegida)
async def chat(entrada: SolicitudChat):
    try:
        return await conversar(entrada)
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
