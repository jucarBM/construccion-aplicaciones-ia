"""Firma y verifica propuestas sin mantener sesiones en el servidor."""

import base64
import hashlib
import hmac
import json
import os

from .configuracion import api_key_esperada


def _secreto() -> bytes:
    return os.getenv("PROPUESTA_SECRET", api_key_esperada()).encode()


def _carga(cliente_id: str, pedido_id: str, motivo: str) -> bytes:
    return json.dumps(
        {"cliente_id": cliente_id, "pedido_id": pedido_id, "motivo": motivo},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()


def emitir_propuesta(cliente_id: str, pedido_id: str, motivo: str) -> str:
    carga = _carga(cliente_id, pedido_id, motivo)
    firma = hmac.new(_secreto(), carga, hashlib.sha256).digest()
    carga_b64 = base64.urlsafe_b64encode(carga).decode().rstrip("=")
    firma_b64 = base64.urlsafe_b64encode(firma).decode().rstrip("=")
    return f"{carga_b64}.{firma_b64}"


def propuesta_valida(token: str, cliente_id: str, pedido_id: str, motivo: str) -> bool:
    try:
        carga_b64, firma_b64 = token.split(".")
        carga = base64.urlsafe_b64decode(carga_b64 + "=" * (-len(carga_b64) % 4))
        firma = base64.urlsafe_b64decode(firma_b64 + "=" * (-len(firma_b64) % 4))
    except (ValueError, TypeError, UnicodeError):
        return False
    esperada = _carga(cliente_id, pedido_id, motivo)
    firma_esperada = hmac.new(_secreto(), esperada, hashlib.sha256).digest()
    return hmac.compare_digest(carga, esperada) and hmac.compare_digest(firma, firma_esperada)
