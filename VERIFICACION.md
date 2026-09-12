# Verificación de los laboratorios independientes

Fecha: 11 de septiembre de 2026, después de migrar a Responses.

Se copió cada laboratorio fuera del repositorio. Las pruebas se ejecutaron por carpeta, en entornos Python 3.12 separados con sus propias dependencias, sin importar código de otra semana.

| Carpeta | Pruebas aprobadas |
|---|---:|
| lab-01 | 8 |
| lab-02 | 21 |
| lab-03 | 24 |
| lab-04 | 25 |
| lab-05 | 26 |
| **Total** | **104** |

Las pruebas usan el SDK de OpenAI con transporte HTTP controlado: comprueban `/v1/responses`, `input`, el formato estructurado y las respuestas vacías o incompletas. Desde LAB-02 comprueban la devolución de resultados mediante `function_call_output`, el vínculo `call_id`, la conservación de elementos de razonamiento y el historial. También cubren permisos, propuestas, confirmación y registros sin duplicados. En LAB-04 y LAB-05 se comprueba el juez Responses con salida estructurada y texto.

El recorrido P-1042 se ejecutó con un modelo controlado y CRM temporal: consulta, seguimiento, propuesta sin escritura, confirmación sin una llamada adicional al modelo, repetición con un único SOL y rechazo de token alterado. Los ejemplos del alumno se ejecutan manualmente en Swagger siguiendo el README de LAB-02.

Captura y evaluación de LAB-04 y LAB-05 respondieron a `--help`. Las pruebas emiten una advertencia de obsolescencia de Starlette/AnyIO que no impide su ejecución.

Alcance: validación local con respuestas controladas. No se realizaron llamadas al proveedor externo, evaluación con juez remoto, construcción Docker, despliegue GCP ni envío de trazas a Langfuse. Estos resultados no verifican esos servicios externos.
