# LAB-02 · Chatbot con herramientas

Sesión 3. Código completo hasta esta semana. Se ejecuta desde esta carpeta, sin importar código de otro laboratorio.

## Preparación

Desde la raíz del repositorio:

```bash
cd lab-02
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

## Práctica

Sigue [los ejemplos para copiar y pegar en Swagger](ejemplos/README.md): consulta P-1042, continúa con historial, reporta el producto distinto y confirma la propuesta. Cada ejemplo explica qué observar y qué cambiar.

## Lectura del código

1. `servicio/main.py`: recibe la petición.
2. `servicio/chat.py`: `conversar` elige entre confirmación y conversación. Las demás funciones preparan los mensajes, la propuesta o las herramientas.
3. `servicio/llm.py`: llama a `cliente.responses.create`.
4. `servicio/herramientas.py` y `servicio/crm.py`: validan, consultan y registran.

Los campos `pedido_id` y `motivo` se escriben explícitamente. El servidor no los conserva entre peticiones. La firma de `seguridad.py` vincula los datos confirmados; no necesitas modificarla para practicar.


[Proyecto del curso](../PROYECTO.md) · [Plantilla de entrega](../PLANTILLA-PROYECTO.md)
