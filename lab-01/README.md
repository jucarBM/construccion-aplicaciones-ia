# LAB-01 · API y clasificación

Sesión 2. Código completo hasta esta semana. Se ejecuta desde esta carpeta, sin importar código de otro laboratorio.

## Preparación

Desde la raíz del repositorio:

```bash
cd lab-01
uv venv .venv --python 3.12
```

Activa el entorno y crea tu configuración **solo la primera vez**:

```bash
# macOS / Linux
source .venv/bin/activate
cp .env.example .env
```

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
```

Edita `.env`: completa `OPENAI_API_KEY` y cambia `API_KEY`. El ejemplo usa OpenAI Responses y `gpt-4o-mini`. `OPENAI_BASE_URL` y `OPENAI_MODEL` permiten otro proveedor que implemente Responses, herramientas y salida estructurada. Una clave de otro proveedor no funciona contra OpenAI.

```bash
uv pip install -r requirements.txt
python -m pytest -q
```

Las pruebas son locales y no consumen el LLM. Para la API:

```bash
python -m uvicorn servicio.main:app --reload --port 8000
```

Abre [Swagger](http://127.0.0.1:8000/docs). Detén el servidor anterior antes de cambiar de lab. En cada operación protegida, pulsa **Try it out**, introduce tu `X-API-Key`, pega el JSON y pulsa **Execute**.


## Objetivo

Ejecutar una API completa, seguir el mensaje desde HTTP hasta el LLM y explicar su respuesta. No hay funciones pendientes de completar. Esta carpeta incluye la solución de la sesión 2.

Completa la [preparación de esta carpeta](#preparación). Todos los comandos se ejecutan dentro de la carpeta del laboratorio que abriste.

## 1. Comprueba el funcionamiento sin proveedor

```bash
python -m pytest -q
```

Las pruebas usan respuestas controladas y no consumen el LLM. Comprueban autenticación, contrato y errores. Después inicia la API:

```bash
python -m uvicorn servicio.main:app --reload --port 8000
```

## 2. Prueba la API

Abre `http://127.0.0.1:8000/docs` y ejecuta en este orden:

1. `GET /salud`: debe responder `{"estado":"ok"}`.
2. `POST /api/clasificar` sin `X-API-Key`: debe responder `401`.
3. Con tu clave de `.env`, envía `{}`: debe responder `422` porque falta `mensaje`.
4. Con clave y credencial del proveedor configuradas, envía:

```json
{"mensaje":"Me llegaron audífonos blancos, pero pedí negros. Necesito resolverlo hoy."}
```

Esta última petición usa el proveedor real. Una respuesta correcta contiene `intencion`, `sentimiento`, `urgencia` y `evidencia`. Revisa qué parte del mensaje respalda cada campo.

## 3. Sigue el código que ya está funcionando

Abre `servicio/main.py` y localiza `clasificar_mensaje`. Después lee `SolicitudClasificacion` y `Clasificacion` en `servicio/contratos.py`, y `clasificar` en `servicio/llm.py`.

Explica el recorrido: validar entrada, llamar al proveedor, validar salida y responder HTTP. El manejo de fallos del proveedor devuelve `503`. Las pruebas permiten observar ese caso sin provocar una llamada real fallida.

## 4. Cambia una entrada y compara

Envía primero un mensaje molesto sin plazo inmediato y después uno neutral que necesita respuesta hoy. Compara sentimiento y urgencia. Vacía el mensaje y observa que falla la validación antes del modelo.

Puedes experimentar con el código de esta carpeta. Tus cambios no alteran las copias de los demás laboratorios. No necesitas copiar funciones para pasar al siguiente.

## Qué conservar

Una clasificación, un `401`, un `422`, el resultado de las pruebas y una explicación breve del recorrido. No muestres claves. La comparación con Flask se trabaja en la sesión; esta aplicación usa FastAPI.


[Proyecto del curso](../PROYECTO.md) · [Plantilla de entrega](../PLANTILLA-PROYECTO.md)
