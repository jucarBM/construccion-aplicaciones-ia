"""Punto de entrada del laboratorio de la sesión 2."""

from fastapi import FastAPI


app = FastAPI(title="Triaje de reclamos")


@app.get("/salud")
def salud():
    return {"estado": "ok"}


# TODO: importe Entrada, Salida y triar.
# TODO: agregue la dependencia de X-API-Key.
# TODO: escriba POST /reclamos y valide también la salida del modelo.
