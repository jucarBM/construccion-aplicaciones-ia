# LAB-03 · Procesamiento por lotes

Sesión 4. Código completo hasta esta semana. Se ejecuta desde esta carpeta, sin importar código de otro laboratorio.

## Preparación

Desde la raíz del repositorio:

```bash
cd lab-03
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

Ejecutar la aplicación completa de LAB-02 más el procesamiento de mensajes TXT. La API, el chatbot y el CRM están incluidos; no necesitas abrir otra carpeta.

Completa la [preparación de esta carpeta](#preparación). El lote funciona desde la terminal y no requiere iniciar Uvicorn.

## 1. Observa el fallo y la reanudación sin proveedor

```bash
python -m pytest -q
python demostraciones.py lote
```

La demostración usa el bucle real con un clasificador controlado y un CRM temporal. A y C terminan, B falla una vez. Al reanudar, solo B se clasifica. Debes observar dos procesados y un error; luego un procesado y dos omitidos. La secuencia de llamadas es A, B, C, B. No modifica tu CRM ni consume el LLM.

## 2. Ejecuta la carpeta de mensajes con el proveedor real

Lee los TXT de `ejemplos/mensajes/` y ejecuta:

```bash
python -m servicio.lote ejemplos/mensajes
```

Esta ejecución llama al LLM para cada entrada pendiente. Abre `crm/analisis/`: cada ANA contiene mensaje, intención, sentimiento, urgencia y evidencia.

Ejecuta el mismo comando otra vez. Los resultados existentes deben aparecer como omitidos, sin volver a llamar al modelo para esas entradas.

## 3. Prueba un cambio y un error

1. Añade `ejemplos/mensajes/mensaje-03.txt` con un texto diferente y ejecuta. Solo esa entrada es nueva.
2. Añade `ejemplos/mensajes/vacio.txt` vacío. Debe aparecer en errores y el bucle debe continuar.
3. Escribe un mensaje válido en ese archivo y reanuda. Lo terminado permanece omitido.

La identidad combina nombre del archivo y mensaje sin espacios exteriores. Cambiar el contenido puede producir un análisis nuevo. Los resultados de otras carpetas lab no cuentan como resultados de esta.

## 4. Explica el bucle existente

Abre `servicio/lote.py`: leer, comprobar resultado, clasificar, guardar y aislar el error. La comprobación de existencia ocurre antes de llamar al LLM. No hay que reconstruir esa función para practicar.

La creación exclusiva de archivos evita reemplazar un resultado. Si dos procesos comprueban a la vez que no existe, ambos podrían llamar al modelo: conservar un ANA no prueba una sola llamada.

## Qué conservar

Los resúmenes de primera ejecución, repetición y recuperación; un ANA y su mensaje; las llamadas de la demostración; una explicación de sentimiento y urgencia basada en el texto.


[Proyecto del curso](../PROYECTO.md) · [Plantilla de entrega](../PLANTILLA-PROYECTO.md)
