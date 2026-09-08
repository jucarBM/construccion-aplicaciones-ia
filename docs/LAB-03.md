# LAB-03 · Construir un lote reanudable

## Objetivo

Reconstruir el bucle que procesa mensajes TXT en orden, guarda cada clasificación terminada y omite resultados existentes antes de llamar al LLM.

La aplicación final queda como referencia. Editarás una sola función en el mismo servicio; una rama personal es opcional.

## Inicio

Activa el entorno y ejecuta:

```bash
pytest -q tests/test_lote_y_crm.py
```

Las pruebas sustituyen el clasificador por uno falso. Por eso miden llamadas, errores e idempotencia sin usar proveedor ni credenciales.

El contrato de salida ya existe en `servicio/contratos.py`:

- `encontrados`: archivos TXT vistos;
- `procesados`: resultados nuevos creados;
- `omitidos`: resultados que ya existían;
- `errores`: archivo y explicación recuperable.

## Edita · Bucle de procesamiento

Abre `servicio/lote.py`, localiza `procesar_carpeta` y reemplaza la función completa por:

```python
async def procesar_carpeta(carpeta: Path) -> ResumenLote:
    if not carpeta.is_dir():
        raise ValueError("La ruta debe ser una carpeta existente.")
    archivos = sorted(carpeta.glob("*.txt"))
    procesados = omitidos = 0
    errores: dict[str, str] = {}
    for archivo in archivos:
        try:
            mensaje = archivo.read_text(encoding="utf-8").strip()
            if not mensaje:
                raise ValueError("mensaje vacío")
            if existe_analisis(archivo.name, mensaje):
                omitidos += 1
                continue
            resultado = await clasificar(mensaje)
            _, creado = guardar_analisis(archivo.name, mensaje, resultado)
            procesados += int(creado)
            omitidos += int(not creado)
        except Exception as error:
            errores[archivo.name] = str(error)
    return ResumenLote(encontrados=len(archivos), procesados=procesados,
                       omitidos=omitidos, errores=errores)
```

Relaciona cada etapa con el código:

1. **Leer:** abre cada `*.txt` ordenado y rechaza el mensaje vacío.
2. **Comprobar:** `existe_analisis` ocurre antes de `await clasificar`.
3. **Clasificar:** solo una entrada pendiente llega al LLM.
4. **Guardar:** `guardar_analisis` crea un ID estable y no reemplaza un resultado.
5. **Aislar:** un error queda en el resumen y el siguiente archivo continúa.

No cambies ese orden: consultar la existencia después de clasificar gastaría otra llamada al reanudar.

## Ejecuta 1 · Prueba medible sin LLM

Repite:

```bash
pytest -q tests/test_lote_y_crm.py
```

La prueba de reanudación exige una sola llamada falsa tras dos ejecuciones. La prueba recuperable exige `["a", "b", "b"]`: el archivo terminado se omite y solo se reintenta el que falló.

## Ejecuta 2 · Carpeta real

Abre `ejemplos/mensajes/` y ejecuta:

```bash
python -m servicio.lote ejemplos/mensajes
```

La primera ejecución consume una llamada LLM por entrada nueva y terminada. Abre `crm/analisis/`: cada `ANA-*.txt` conserva mensaje, intención, sentimiento, urgencia y evidencia.

Ejecuta el mismo comando otra vez. Los archivos existentes deben aparecer como `omitidos`; no deben crearse registros nuevos ni hacerse otra llamada LLM para ellos.

## Ejecuta 3 · Cambio, fallo y reanudación

1. Crea `ejemplos/mensajes/mensaje-03.txt` con un mensaje diferente. Solo esa entrada debe quedar `procesada`.
2. Agrega temporalmente `ejemplos/mensajes/vacio.txt`. Debe aparecer en `errores` sin impedir que los demás resultados sigan disponibles.
3. Escribe un mensaje válido en `vacio.txt` y reintenta. Los anteriores quedan `omitidos` y ese archivo pasa a `procesados`.

El sentimiento describe el texto; no concede prioridad comercial, permisos ni derechos distintos al cliente.

## Esperado y evidencia

Guarda:

1. el fragmento editado o su diff;
2. la prueba sin LLM y su contador implícito de llamadas;
3. resúmenes de primera ejecución, repetición y recuperación;
4. el mensaje nuevo y su `ANA-*.txt`;
5. una tabla pequeña con llamadas esperadas: primera ejecución = entradas nuevas; repetición = 0; recuperación = archivos pendientes.

No entregues `.env` ni caches. Los `ANA-*.txt` contienen datos didácticos; en un caso propio elimina información personal innecesaria.
