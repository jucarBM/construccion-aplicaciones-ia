# LAB-01 · Construir una API de clasificación

## Objetivo

Reconstruir dos piezas pequeñas de la aplicación de referencia: el contrato de entrada y el endpoint que llama al LLM. Después comprobarás `200`, `401`, `422` y el manejo del proveedor sin depender de pruebas pagadas.

Completa la [preparación común](../README.md#preparación-común). El repositorio ya contiene la solución final para que siempre tengas una referencia ejecutable. Si quieres conservar tus ediciones, trabaja en una rama personal; no es obligatorio para completar la práctica.

## Inicio

Desde la raíz de `labs/`, ejecuta la comprobación inicial. Estas pruebas sustituyen el proveedor por una respuesta controlada y no consumen el LLM:

```bash
pytest -q tests/test_api.py -k "clasificacion or proveedor or rutas_api"
```

Debes obtener pruebas aprobadas. Si no ocurre, guarda el error antes de editar: será tu línea base.

## Edita 1 · Contrato de entrada

Abre `servicio/contratos.py`, localiza `SolicitudClasificacion` y reemplaza esa clase completa por:

```python
class SolicitudClasificacion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mensaje: TextoBreve
```

`TextoBreve` ya está definido en el mismo archivo: elimina espacios exteriores, exige contenido y limita su longitud. `extra="forbid"` rechaza campos que no pertenecen al contrato. No crees otro modelo ni otro archivo.

## Edita 2 · Endpoint

Abre `servicio/main.py`, localiza `clasificar_mensaje` y reemplaza el decorador y la función completa por este bloque:

```python
@app.post("/api/clasificar", response_model=Clasificacion, dependencies=protegida)
async def clasificar_mensaje(entrada: SolicitudClasificacion):
    try:
        with observacion("Clasificar mensaje", entrada.model_dump()) as span:
            resultado = await clasificar(entrada.mensaje)
            if span:
                span.update(output=resultado.model_dump())
            return resultado
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
```

Los imports, `protegida`, `observacion` y `clasificar` ya existen en la aplicación de referencia. El flujo queda así:

1. FastAPI recibe JSON y `SolicitudClasificacion` valida la entrada.
2. El handler entrega solo `mensaje` a `clasificar`.
3. `servicio/llm.py` llama al proveedor y valida la salida como `Clasificacion`.
4. FastAPI serializa ese contrato como JSON; un fallo controlado del proveedor se convierte en `503`.

## Ejecuta

Repite la prueba local sin costo:

```bash
pytest -q tests/test_api.py -k "clasificacion or proveedor or rutas_api"
```

Luego inicia la aplicación:

```bash
python -m uvicorn servicio.main:app --reload --port 8000
```

Abre `http://127.0.0.1:8000/docs` y ejecuta en este orden:

1. `GET /salud`: debe responder `{"estado":"ok"}` sin credencial.
2. `POST /api/clasificar` sin `X-API-Key`: debe responder `401`.
3. El mismo endpoint con clave y cuerpo `{}`: debe responder `422` porque falta `mensaje`.
4. Con clave, envía una petición real:

```json
{
  "mensaje": "Me llegaron audífonos blancos, pero pedí negros. Necesito resolverlo hoy."
}
```

La respuesta `200` debe contener `intencion`, `sentimiento`, `urgencia` y `evidencia`. Esta última petición sí consume una llamada al proveedor. La evidencia debe apoyarse en el mensaje; no basta una etiqueta inventada.

Como lectura adicional, compara el decorador y la validación automática de FastAPI con el fragmento Flask mostrado en la sesión. El laboratorio mantiene un solo servicio ejecutable: no construyas una segunda aplicación Flask.

## Esperado y evidencia

Guarda:

1. el fragmento editado o su diff;
2. la prueba local aprobada;
3. una clasificación completa;
4. un `401` sin mostrar la clave;
5. un `422` que muestre el campo inválido.

Explica en dos frases dónde termina la validación del contrato y dónde comienza la llamada al LLM. No incluyas `.env`, claves ni encabezados completos en las capturas.
