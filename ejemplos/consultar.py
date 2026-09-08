"""Ejemplo corto contra la API en ejecución."""

import os

import httpx


base = os.getenv("API_URL", "http://127.0.0.1:8000")
headers = {"X-API-Key": os.getenv("API_KEY", "curso-local")}
with httpx.Client(base_url=base, headers=headers, timeout=60) as cliente:
    print(cliente.get("/api/pedidos/P-1042").json())
    print(cliente.post("/api/clasificar", json={"mensaje": "¿Dónde está P-1043?"}).json())
