# LAB-04 · Captura y evaluación

## Objetivo

Evaluar respuestas y herramientas observadas en la API real, completar el checklist de salida de S5 y probar localmente el contenedor candidato. Primero usarás una comparación determinista, sin juez LLM; el juez semántico es una extensión opcional y pagada.

## 1. Instala la extensión de evaluación

Activa `.venv` e instala:

```bash
uv pip install -r requirements-evaluacion.txt
```

En otra terminal, activa el mismo entorno e inicia FastAPI. Comprueba `/salud` antes de capturar.

## 2. Lee los casos antes de ejecutarlos

Abre `evaluacion/casos.json`. Incluye estado de pedido, dato faltante y pedido ajeno. Este último es un **caso negativo intencionado**: la conducta correcta es no encontrarlo dentro del cliente de demostración y no revelar datos.

## 3. Captura el sistema real

Crea una carpeta local para evidencia y elige un nombre nuevo en cada ejecución:

```bash
mkdir -p evidencia/lab-04
python evaluacion/capturar.py \
  --salida evidencia/lab-04/capturas-01.jsonl
```

En PowerShell, escribe el comando en una sola línea. `capturar.py` llama a `/api/chat` y guarda respuesta, latencia, `trace_id` y solo las herramientas realmente devueltas por la API. No reemplaza esas llamadas con una lista esperada.

Abre el JSONL y revisa los tres registros antes de evaluar. Si repites, usa `capturas-02.jsonl`: el script no sobreescribe evidencia anterior.

## 4. Ejecuta la métrica determinista

```bash
python evaluacion/evaluar.py \
  --archivo evidencia/lab-04/capturas-01.jsonl \
  --salida evidencia/lab-04/resultados-deterministas-01.jsonl
```

Sin `--juez`, DeepEval compara nombre y argumentos de herramientas con coincidencia exacta y no consume un modelo evaluador. Un fallo indica una diferencia observable: abre la captura, el caso esperado y la razón antes de cambiar el código.

El caso negativo `pedido_ajeno` puede aprobar: «negativo» describe la entrada de seguridad, no el resultado de la métrica.

## 5. Extensión opcional con juez

Si el docente autoriza costo y tienes credenciales, configura `EVAL_MODEL` y ejecuta:

```bash
python evaluacion/evaluar.py \
  --archivo evidencia/lab-04/capturas-01.jsonl \
  --salida evidencia/lab-04/resultados-juez-01.jsonl \
  --juez
```

El juez compara la respuesta con referencia, contexto y resultados reales. Su puntaje no sustituye tu revisión: lee la razón y comprueba que no afirme una aprobación o reembolso inexistente.

## 6. Completa el checklist de S5

Abre [PLANTILLA-PROYECTO.md](../PLANTILLA-PROYECTO.md) y completa estas secciones con tu aplicación:

1. **Casos de validación:** al menos cinco, incluidos funcionamiento, dato faltante, error, seguridad y repetición.
2. **Resultados:** rutas de capturas e informe, fallos encontrados y límites abiertos.
3. **Despliegue y observabilidad:** persistencia, endpoint previsto, costo disponible y acción de cierre.
4. **Entrega final:** marca solo lo que tenga evidencia; registra el resto como pendiente con una acción.

Los tres casos de `evaluacion/casos.json` cubren estado, dato faltante y seguridad. Usa además la propuesta sin escritura y la confirmación alterada de LAB-02 para completar cinco comportamientos del caso guía. En un proyecto propio, los cinco casos deben corresponder a su API y sus datos.

## 7. Prueba el contenedor candidato

Construye un contexto temporal que incluya solo código, dependencias y los dos TXT de referencia:

```bash
export BUILD_DIR="$(mktemp -d)"
cp Dockerfile requirements.txt requirements-despliegue.txt "$BUILD_DIR/"
cp -R servicio "$BUILD_DIR/servicio"
mkdir "$BUILD_DIR/crm"
cp crm/pedidos.txt crm/politicas.txt "$BUILD_DIR/crm/"
docker build -t tienda-ia:s5 "$BUILD_DIR"
```

Arranca la imagen sin `.env` y verifica salud, contrato y acceso:

```bash
docker run --rm -d --name tienda-ia-s5 -p 8080:8080 tienda-ia:s5
curl -fsS "http://127.0.0.1:8080/salud"
curl -fsS "http://127.0.0.1:8080/openapi.json" | jq '.paths | keys'
curl -sS -o /dev/null -w '%{http_code}\n' \
  "http://127.0.0.1:8080/api/pedidos/P-1042"
docker stop tienda-ia-s5
rm -rf -- "$BUILD_DIR"
```

Debes observar `{"estado":"ok"}`, las rutas del contrato y `401` en la ruta protegida. Esta prueba no llama al LLM ni demuestra GCP. Si Docker o `jq` no están disponibles, registra el bloqueo y el comando pendiente; no marques el contenedor como probado.

Mantén `LANGFUSE_ENABLED=false` durante esta evaluación si quieres aislar la métrica y el contenedor. Puedes ensayar Langfuse localmente, pero la evidencia final de traza es obligatoria en LAB-05 y en el proyecto. Si no tienes credenciales, coordina la ejecución guiada indicada allí.

## Evidencia

Entrega el JSONL de capturas, el informe determinista, un comentario breve por caso, el checklist S5 y la evidencia del contenedor local. Si usaste juez, separa sus resultados, modelo y costo aproximado. Nunca incluyas claves ni un `.env`.
