# Laboratorios · Construcción de aplicaciones impulsadas por IA

Durante cinco prácticas ampliarás una sola aplicación de soporte para pedidos y devoluciones. El caso usa registros TXT fáciles de inspeccionar; las llamadas al LLM, las consultas y las escrituras ejecutadas por la aplicación son reales.

Lee primero [el caso y sus límites](docs/CASO.md). Tu proyecto puede usar otro problema y otras fuentes de datos.

## Recorrido de las prácticas

| Sesión | Guía | Resultado |
|---|---|---|
| 2 | [LAB-01](docs/LAB-01.md) | API, validación y clasificación estructurada. |
| 3 | [LAB-02](docs/LAB-02.md) | Conversación, herramientas y escritura confirmada. |
| 4 | [LAB-03](docs/LAB-03.md) | Lote secuencial, sentimiento e idempotencia. |
| 5 | [LAB-04](docs/LAB-04.md) | Capturas reales y evaluación con DeepEval. |
| 6 | [LAB-05](docs/LAB-05.md) | Contenedor, GCP y trazas en Langfuse. |

El trabajo integrador está en [PROYECTO.md](PROYECTO.md). Usa [PLANTILLA-PROYECTO.md](PLANTILLA-PROYECTO.md) para registrar decisiones y avances.

## Preparación común

Ejecuta todos los comandos desde la raíz de este repositorio.

```bash
uv venv .venv
```

Activa el entorno:

```bash
# macOS o Linux
source .venv/bin/activate
```

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Instala las dependencias y crea tu configuración local:

```bash
uv pip install -r requirements.txt
cp .env.example .env
```

Si prefieres `pip`, usa `python -m pip install -r requirements.txt`. En PowerShell, reemplaza el comando de copia por `Copy-Item .env.example .env`. Edita `.env`, cambia `API_KEY` y `PROPUESTA_SECRET`, y completa las credenciales del proveedor LLM. Si usas OpenRouter, conserva `OPENAI_BASE_URL=https://openrouter.ai/api/v1` y elige un modelo disponible de bajo costo.

No compartas ni captures claves. `.env` está excluido de Git; `.env.example` solo contiene nombres y valores de ejemplo. La fecha `FECHA_ESCENARIO=2026-09-08` fija el estado del CRM simulado y no representa la fecha anual del curso. Conserva `LANGFUSE_ENABLED=false` hasta el LAB-05; las trazas son opcionales durante el desarrollo local y se comprueban en la sesión 6.

Inicia la aplicación:

```bash
python -m uvicorn servicio.main:app --reload --port 8000
```

Abre `http://127.0.0.1:8000/docs`. En las rutas `/api/*`, usa el valor local de `API_KEY` en el campo `X-API-Key`. `GET /salud` y la documentación son públicos.

## Mapa del código

- `servicio/main.py`: rutas HTTP.
- `servicio/contratos.py`: entradas y salidas Pydantic.
- `servicio/llm.py`: llamadas al modelo.
- `servicio/chat.py`: conversación e historial.
- `servicio/herramientas.py`: herramientas permitidas y controles.
- `servicio/crm.py`: lectura y escritura TXT o Cloud Storage.
- `servicio/lote.py`: procesamiento secuencial de mensajes.
- `crm/`: datos didácticos legibles.
- `evaluacion/`: casos, captura y evaluación.

Cada práctica empieza cambiando mensajes o datos pequeños. Modifica código solo donde la guía lo indique. Antes de entregar evidencia, abre cada captura y confirma que se leen la entrada, la salida y el comportamiento observado, sin claves ni tokens completos.
