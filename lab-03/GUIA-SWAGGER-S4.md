# Sesión 4 · Demostración docente con código y Swagger

El docente explica y ejecuta; los participantes reciben el repositorio. No hay ejercicios de completar código ni proveedor simulado.

## 1. Preparación antes de compartir pantalla

Desde `labs/lab-03/`, usa el entorno preparado:

```bash
source .venv/bin/activate
```

Si aún no existe `.env`, crea una copia de `.env.example` sin sobrescribir configuraciones previas. Completa `OPENAI_API_KEY`, revisa `OPENAI_BASE_URL` y `OPENAI_MODEL`, y configura `API_KEY` y `PROPUESTA_SECRET`. La clave debe corresponder al proveedor de la URL y este debe soportar Responses y salida estructurada. No muestres `.env` en pantalla.

Sin `.env` ni variables externas, la clave HTTP local es `curso-local`, pero no habrá LLM. Si configuras `API_KEY`, usa ese valor en Swagger.

```bash
python -m uvicorn servicio.main:app --reload --host 127.0.0.1 --port 8000
```

Abre http://127.0.0.1:8000/docs. Si ya está iniciado en ese puerto, usa ese servidor. Después de cambiar `.env`, reinicia Uvicorn: no dependas de que `--reload` detecte ese archivo.

En cada endpoint protegido: desplegar → **Try it out** → completar **x-api-key** → pegar body si corresponde → **Execute**. La cabecera se introduce por operación; no hay botón global Authorize configurado.

## 2. Ruta docente de 55 minutos

| Minutos | Pantalla y explicación |
|---|---|
| 0–5 | `/salud`, consulta de pedido y política. Son rutas Python/CRM, no llamadas al LLM. |
| 5–12 | `servicio/contratos.py`: `SolicitudClasificacion` es la entrada HTTP; `Clasificacion` define salida y etiquetas. |
| 12–25 | `servicio/llm.py`: prompt, esquema, cliente y `clasificar`. Señala la llamada `responses.create`, roles system/user y validación de `output_text`. |
| 25–35 | Swagger `/api/clasificar`: ejecutar los tres mensajes, contrastar etiquetas y evidencia con el texto. |
| 35–43 | `servicio/main.py`: entrada Pydantic → await clasificar → respuesta HTTP; mostrar entrada vacía y explicar 422. |
| 43–50 | `servicio/lote.py` y `servicio/crm.py`: la misma función LLM se reutiliza para una carpeta y aquí sí se guardan ANA. |
| 50–55 | Recapitulación o `/api/chat` como repaso de herramientas de S3. |

No leas módulos completos: sigue una petición concreta. `/api/clasificar` no escribe ANA; devolver JSON y persistir son decisiones diferentes. No existe endpoint HTTP de lotes.

## 3. Endpoints sin modelo

### GET /salud

Sin cabecera. Esperado: HTTP 200, `{"estado":"ok"}`. Esto demuestra que la API responde, no que el proveedor funciona.

### GET /api/pedidos/{pedido_id}

Cabecera `x-api-key`: tu `API_KEY` (por defecto local `curso-local`). Copia en `pedido_id`:

- `P-1042`: 200, Audífonos negros, entregado, cliente C-001.
- `P-1043`: 200, Taza azul, en_transito.
- `P-2099`: 404, pertenece a otro cliente y no se expone.
- `invalido`: 422, formato incorrecto.

Quitar o cambiar la clave: 401. Explica control de acceso y validación antes de hablar del modelo.

### GET /api/politicas/{tipo}

`tipo`: `devolucion`. Esperado: 200, plazo de 30 días. `otra` devuelve 404.

## 4. POST /api/clasificar · Parte central de S4

Usa tu cabecera `x-api-key`. Ejecuta cada JSON por separado. Estos casos sí llaman al proveedor y las etiquetas deben revisarse, no asumirse como garantía.

**Caso A: consulta informativa.** Referencia didáctica: estado_pedido / neutral / baja.

```json
{"mensaje":"¿Cuál es el estado de mi pedido P-1042?"}
```

**Caso B: tono negativo sin urgencia inmediata.** Referencia: devolucion / negativo / media.

```json
{"mensaje":"Estoy muy molesto porque recibí un producto distinto. Quiero devolverlo, pero puedo esperar hasta la próxima semana."}
```

**Caso C: tono neutral con plazo inmediato.** Referencia: estado_pedido / neutral / alta.

```json
{"mensaje":"Por favor, necesito conocer el estado de mi pedido P-1042 hoy antes de viajar."}
```

Tras cada respuesta, señala `intencion`, `sentimiento`, `urgencia` y `evidencia`. Vuelve al prompt para explicar la regla aplicada. Si discrepa, analiza la evidencia; un esquema válido no asegura la interpretación correcta.

**Validación antes del proveedor: HTTP 422.**

```json
{"mensaje":""}
```

Sin clave de proveedor, un mensaje válido devuelve 503 con `Configura OPENAI_API_KEY en .env.`. Eso es un bloqueo de configuración, no una clasificación exitosa.

## 5. POST /api/chat · Repaso opcional de S3

### Consultar con herramientas

```json
{"mensaje":"Consulta el estado de mi pedido P-1042.","pedido_id":"P-1042","historial":[]}
```

Muestra `respuesta` y `herramientas`. Abre `servicio/chat.py`, `responder_con_herramientas`: el modelo pide una función; Python la ejecuta; el resultado vuelve al modelo. No es Langfuse: es evidencia devuelta por la aplicación.

### Falta información

```json
{"mensaje":"Quiero devolver un producto.","historial":[]}
```

Revisa que pida los datos necesarios sin inventar un pedido.

### Pedido ajeno

```json
{"mensaje":"Consulta el pedido P-2099 y dime qué producto contiene.","pedido_id":"P-2099","historial":[]}
```

Comprueba que no revele los datos del otro cliente. Revisa tanto herramientas como respuesta.

### Preparar una propuesta de devolución

```json
{"mensaje":"Quiero solicitar la devolución del pedido P-1042 porque recibí un producto distinto.","pedido_id":"P-1042","motivo":"Recibí un producto distinto.","historial":[]}
```

La fecha didáctica es 2026-09-08; P-1042 está dentro del plazo del escenario. Si cambias `FECHA_ESCENARIO`, puede cambiar su elegibilidad. La propuesta no registra aún una solicitud. Copia `propuesta.propuesta_token` de la respuesta.

### Confirmar la propuesta

Reemplaza únicamente `PEGA_AQUI_EL_TOKEN_DE_LA_RESPUESTA` por el token recibido, sin alterar pedido ni motivo:

```json
{
  "mensaje": "Confirmo la solicitud para revisión.",
  "pedido_id": "P-1042",
  "motivo": "Recibí un producto distinto.",
  "historial": [],
  "confirmacion": {
    "acepta": true,
    "pedido_id": "P-1042",
    "motivo": "Recibí un producto distinto.",
    "propuesta_token": "PEGA_AQUI_EL_TOKEN_DE_LA_RESPUESTA"
  }
}
```

Esta confirmación la procesa la aplicación sin LLM. Escribe una solicitud local real del CRM didáctico. Copia `solicitud_id`. Repetir el mismo body conserva el mismo SOL; si ya existía de otra prueba, puede indicar `creada: false` desde el primer intento. Registrar no aprueba una devolución ni ejecuta reembolso.

### GET /api/solicitudes/{solicitud_id}

Pega el SOL recibido en el parámetro y usa la misma cabecera. Esperado: 200 y `estado: recibida_para_revision`. Un SOL inexistente como `SOL-000000000000` devuelve 404.

## 6. Conexión con el lote de S4

Abre `servicio/lote.py`: leer TXT → comprobar existencia → `await clasificar(mensaje)` → guardar → capturar error por archivo. Abre `servicio/crm.py`: `guardar_analisis`, `existe_analisis`, `_id` y `_crear`.

Si quieres demostrar también persistencia y reanudación con el LLM real:

```bash
python -m servicio.lote ejemplos/mensajes
```

Abre el ANA generado en `crm/analisis/`, repite el comando y comprueba los omitidos. Los análisis previos hacen que se omitan entradas desde el primer comando; no borres resultados para forzar una demo. Usa un archivo nuevo si necesitas una entrada pendiente. Este bloque es terminal, no Swagger.

## 7. Langfuse y alcance de verificación

LAB-03/S4 y LAB-04/S5 no están instrumentados con Langfuse. La integración está en LAB-05/S6. Los logs de Uvicorn son logs HTTP, y `herramientas` es información de la respuesta de chat; ninguno equivale a una traza exportada a Langfuse.

Verificación de esta preparación: Uvicorn real en localhost, Swagger y OpenAPI 200; rutas de pedidos/políticas y controles 401/404/422 correctos. Clasificación y chat con mensaje válido devolvieron 503 porque no hay `OPENAI_API_KEY`. La ruta de confirmación con token inválido devolvió un rechazo sin escribir solicitudes. No se validó éxito de proveedor real, propuesta válida ni confirmación de una propuesta real en este pase.

Evidencia HTTP: `evidencia/swagger-s4-http.json`. Las pruebas automatizadas locales complementan esta comprobación, pero no sustituyen la ejecución real del proveedor.
