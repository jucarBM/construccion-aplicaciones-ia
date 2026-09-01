"""La conversación de la sesión 3.

La memoria la guarda esta aplicación, no el modelo: cada llamada sale en
blanco, así que el historial hay que armarlo y mandarlo entero. Y como cada
turno reenvía todo lo anterior, recortarlo es parte del diseño.
"""

import os
import sqlite3
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from app import trazas
from app.modelo import MODELO, cliente

router = APIRouter()

# Los últimos seis turnos. Es la decisión de diseño de la lámina: barata de
# implementar, y olvida de golpe lo que se dijo al principio.
VENTANA = 6

REGLAS = """Eres el asistente de la bandeja de atención.

QUÉ HACES
- Respondes dudas sobre el estado de un caso.
- Pides los datos que falten, de a uno por vez.

QUÉ NO HACES NUNCA
- No prometes plazos, montos ni devoluciones.
- No inventas datos: si no los tienes, los pides.
- No hablas de otros temas que no sean el caso.

CUÁNDO SALES
Si piden un monto, una baja o insisten dos veces con lo mismo, dices que lo
pasas a una persona. Lo dices explícitamente: un cliente que sabe que lo
derivan espera, uno que siente que lo esquivan se enoja."""


class Turno(BaseModel):
    conv_id: str
    texto: str


class Respuesta(BaseModel):
    texto: str
    derivar: bool = False


def _bd():
    c = sqlite3.connect(os.getenv("BD_CHAT", "conversaciones.sqlite"))
    c.execute(
        "CREATE TABLE IF NOT EXISTS turnos ("
        "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "  conv_id TEXT, rol TEXT, texto TEXT,"
        "  fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    )
    return c


def historial(conv_id: str) -> list[dict]:
    with _bd() as c:
        filas = c.execute(
            "SELECT rol, texto FROM turnos WHERE conv_id = ? ORDER BY id", (conv_id,)
        ).fetchall()
    return [{"role": rol, "content": texto} for rol, texto in filas]


def guardar(conv_id: str, rol: Literal["user", "assistant"], texto: str) -> None:
    with _bd() as c:
        c.execute(
            "INSERT INTO turnos (conv_id, rol, texto) VALUES (?, ?, ?)",
            (conv_id, rol, texto),
        )


@router.post("/chat", response_model=Respuesta)
def chat(e: Turno) -> Respuesta:
    hist = historial(e.conv_id)[-VENTANA:]
    msgs = (
        [{"role": "system", "content": REGLAS}]
        + hist
        + [{"role": "user", "content": e.texto}]
    )

    with trazas.span_modelo(MODELO) as span:
        r = cliente.chat.completions.create(
            model=MODELO, temperature=0.4, messages=msgs
        )
        span.anotar_uso(r)

    texto = r.choices[0].message.content

    # Las respuestas propias también van al historial. Si no, el bot se
    # contradice a sí mismo dos turnos después.
    guardar(e.conv_id, "user", e.texto)
    guardar(e.conv_id, "assistant", texto)

    return Respuesta(texto=texto, derivar="paso a una persona" in texto.lower())
