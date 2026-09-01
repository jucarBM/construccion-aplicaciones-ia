# Triaje de reclamos

El sistema que se construye a lo largo de las seis sesiones de **Construcción
de Aplicaciones Impulsadas por IA**. Una empresa recibe 300 mensajes diarios en
texto libre; esto los clasifica, los procesa por lote, se mide y se despliega.

No hay que escribirlo en clase. Cada sesión usa la parte que le toca.

| Sesión | Archivo | Qué se hace |
|---|---|---|
| 2 · APIs | `app/esquemas.py`, `app/modelo.py`, `app/main.py` | El endpoint, la validación de ida y vuelta, la clave |
| 3 · Chatbots | `app/chat.py` | Historial, recorte, prompt de sistema, salida a humano |
| 4 · Automatización | `app/lote.py`, `datos/reclamos.jsonl` | Lote con tope de paralelo, estado por mensaje, ensayo en seco |
| 5 · Evaluación | `evals/` | Conjunto congelado, acierto, juez con criterios, camino del agente |
| 6 · Despliegue | `app/trazas.py`, `Dockerfile`, `despliegue/` | OpenTelemetry a Langfuse, contenedor, Cloud Run |

## Arrancar

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # completar OPENROUTER_API_KEY y API_KEY
uvicorn app.main:app --reload
```

Y en otra terminal:

```bash
curl -s -X POST localhost:8000/reclamos \
  -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  -d '{"id":"RCL-001","texto":"Me cobraron dos veces la factura de marzo.","canal":"correo"}'
```

Sin la cabecera devuelve 401. Con el texto vacío, 422. Los dos son a propósito.

## El lote

```bash
python -m app.lote datos/reclamos.jsonl --dry-run   # dice qué haría
python -m app.lote datos/reclamos.jsonl             # lo hace
```

Se puede cortar con Ctrl-C y volver a correrlo: retoma donde quedó, porque cada
mensaje guarda su estado. Correrlo dos veces no duplica nada.

## La evaluación

```bash
pytest evals/ -q                  # rápido
deepeval test run evals/          # con el informe de DeepEval
```

`test_area` y `test_acierto_global` comparan con `==` y corren solo con la
clave del servicio. `test_evidencia` usa GEval con criterios en castellano y
necesita además `OPENAI_API_KEY`, la del modelo juez; sin ella se salta sola,
igual que `test_camino`, porque DeepEval pide esa clave para arrancar aunque
la métrica no juzgue con modelo.

El conjunto de `evals/conjunto.jsonl` está congelado. Si se le agregan casos
cada vez que algo falla, los números dejan de ser comparables entre corridas.

## Las trazas

Con `LANGFUSE_PUBLIC_KEY` y `LANGFUSE_SECRET_KEY` puestas, cada petición
aparece en Langfuse con sus tramos y sus tokens. Sin ellas y con
`TRAZAS=consola`, la traza sale por pantalla. Sin ninguna de las dos, no se
exporta nada y el servicio anda igual: es lo que conviene en las sesiones 2 a 5.

El plan Hobby de Langfuse es gratis y no pide tarjeta.

Las convenciones `gen_ai` de OpenTelemetry todavía están en desarrollo y no son
estables. Los atributos de chat que se usan acá son firmes; los de agentes se
siguen moviendo.

## Desplegar

Paso a paso en [`despliegue/README.md`](despliegue/README.md), con Cloud Run y
Secret Manager.
