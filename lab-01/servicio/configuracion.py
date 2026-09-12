"""Configuración local y autenticación de esta carpeta."""

import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Header, HTTPException


RAIZ = Path(__file__).resolve().parents[1]
load_dotenv(RAIZ / ".env")


def api_key_esperada() -> str:
    clave = os.getenv("API_KEY")
    if clave:
        return clave
    return "curso-local"


def exigir_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if not x_api_key or not secrets.compare_digest(x_api_key, api_key_esperada()):
        raise HTTPException(status_code=401, detail="Credencial inválida.")
