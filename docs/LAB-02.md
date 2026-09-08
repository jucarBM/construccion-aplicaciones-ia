# LAB-02 · Construir conversación y herramientas

## Objetivo

Reconstruir la función que arma el contexto conversacional, comprobar el límite del historial y ejecutar una consulta y una escritura protegida por confirmación estructurada.

Inicia desde la solución final del repositorio. Puedes conservar tu trabajo en una rama personal, pero la práctica no requiere crear otra aplicación ni copiar todo `chat.py`.

## Inicio

Activa el entorno y ejecuta pruebas sin proveedor:

```bash
pytest -q tests/test_api.py -k "historial or confirmacion or modelo_no_puede"
```

Estas pruebas usan un LLM falso y un CRM temporal. Verifican límites y escritura sin consumir una llamada pagada.

## Edita · Construcción del historial

Abre `servicio/chat.py`, localiza `_mensajes` y reemplaza solo esa función por el bloque final siguiente:

```python
def _mensajes(entrada: SolicitudChat) -> list[dict]:
    historial = entrada.historial[-8:]
    mensajes = [{"role": "system", "content": SISTEMA}]
    mensajes.extend({"role": turno.rol.replace("usuario", "user").replace("asistente", "assistant"),
                     "content": turno.contenido} for turno in historial)
    contexto = {"mensaje": entrada.mensaje, "pedido_id": entrada.pedido_id, "motivo": entrada.motivo,
                "confirmacion_http": entrada.confirmacion is not None}
    mensajes.append({"role": "user", "content": json.dumps(contexto, ensure_ascii=False)})
    return mensajes
```

Lee el bloque en tres incrementos pequeños:

1. `entrada.historial[-8:]` retiene los ocho turnos más recientes.
2. Los roles del contrato HTTP se convierten a los roles que acepta el proveedor.
3. El mensaje actual, pedido, motivo y presencia de confirmación viajan juntos como datos del usuario.

La función no decide permisos. La escritura sigue controlada por `conversar` y `herramientas.py`; el token de propuesta no se añade a los mensajes del modelo.

## Ejecuta 1 · Límite del historial

Repite las pruebas:

```bash
pytest -q tests/test_api.py -k "historial or modelo_y_traza"
```

El caso de 13 turnos debe producir `422` por el contrato. Con hasta 12 turnos la petición es válida, pero `_mensajes` conserva solo los últimos ocho antes del mensaje actual.

Inicia FastAPI como indica el [README](../README.md#preparación-común). En `POST /api/chat`, usa:

```json
{
  "mensaje": "Me llegó otro producto y quiero devolverlo."
}
```

La respuesta debe pedir el pedido que falta y `herramientas` debe estar vacío. En la siguiente petición puedes incluir los turnos anteriores en `historial`, con roles `usuario` y `asistente`.

## Ejecuta 2 · Propuesta sin escritura

Envía:

```json
{
  "mensaje": "Me llegaron audífonos blancos en vez de negros.",
  "pedido_id": "P-1042",
  "motivo": "Recibí un producto distinto"
}
```

La aplicación consulta el pedido y la política antes de devolver `propuesta`. Cada elemento de `herramientas` muestra nombre, argumentos, resultado y origen. Todavía no debe existir un nuevo `SOL-*.txt`.

El servidor trabaja con el cliente fijo `C-001`. Escribir un ID no demuestra identidad; `P-2099` pertenece a otro cliente y no debe revelar sus datos.

## Ejecuta 3 · Confirmación y negativo

Copia `propuesta_token` y devuelve exactamente el mismo pedido y motivo:

```json
{
  "mensaje": "Confirmo la propuesta.",
  "pedido_id": "P-1042",
  "motivo": "Recibí un producto distinto",
  "confirmacion": {
    "acepta": true,
    "pedido_id": "P-1042",
    "motivo": "Recibí un producto distinto",
    "propuesta_token": "PEGA_AQUI_EL_TOKEN"
  }
}
```

La respuesta entrega `solicitud_id` y estado `recibida_para_revision`. Consulta `GET /api/solicitudes/{solicitud_id}` y repite exactamente la confirmación: debe conservar el identificador y mostrar `creada: false`.

Ahora altera un carácter del token y vuelve a enviar la confirmación. Debe aparecer `confirmacion_http_valida_requerida`, no debe haber `solicitud_id` y no debe crearse otro TXT. Un «sí» dentro de `mensaje` tampoco habilita la escritura.

## Esperado y evidencia

Guarda:

1. el fragmento editado o su diff;
2. las pruebas con LLM falso;
3. la petición con historial y el dato faltante;
4. la propuesta sin escritura;
5. el registro, su lectura y la repetición idempotente;
6. el negativo con token alterado.

Oculta la clave y la mayor parte del token. Conserva visibles pedido, motivo, herramientas, identificador y `creada`.
