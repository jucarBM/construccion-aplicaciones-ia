"""Consulta y confirma una solicitud mediante dos cuerpos HTTP explícitos."""

import os

import httpx


base = os.getenv("API_URL", "http://127.0.0.1:8000")
headers = {"X-API-Key": os.getenv("API_KEY", "curso-local")}
datos = {"mensaje": "Recibí unos audífonos blancos", "pedido_id": "P-1042",
         "motivo": "Recibí un producto distinto"}
with httpx.Client(base_url=base, headers=headers, timeout=60) as cliente:
    propuesta = cliente.post("/api/chat", json=datos).json()
    print(propuesta)
    datos["mensaje"] = "Confirmo que deseo registrar la solicitud"
    datos["confirmacion"] = {"acepta": True, "pedido_id": datos["pedido_id"],
                              "motivo": datos["motivo"],
                              "propuesta_token": propuesta["propuesta"]["propuesta_token"]}
    print(cliente.post("/api/chat", json=datos).json())
