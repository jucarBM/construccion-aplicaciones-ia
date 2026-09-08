# Proyecto individual del curso

Construirás y demostrarás una aplicación impulsada por IA que resuelva un recorrido útil de principio a fin. Puedes elegir libremente el caso; pedidos y devoluciones es una guía disponible, no una obligación.

El proyecto vale **40% de la nota del curso**. Los otros componentes son participación 10%, cuestionarios 20% y talleres 30%.

## Resultado mínimo

Tu aplicación debe incluir:

1. una API con contratos de entrada, salida y error;
2. una llamada LLM con salida controlada y límites de consumo;
3. conversación y al menos una operación conectada a datos o a otro sistema;
4. un control explícito antes de una escritura o acción sensible;
5. automatización de un lote reanudable;
6. clasificación de sentimiento o de otra magnitud adecuada al proceso, con la elección justificada;
7. al menos cinco casos diversos que incluyan funcionamiento, dato faltante, error y seguridad;
8. capturas del sistema real, evaluación con DeepEval y evidencia de herramientas cuando aplique;
9. trazas en Langfuse y despliegue verificable en GCP.

Registrar una intención no equivale a completar una acción de negocio. Explica qué consulta, qué propone, qué escribe y qué queda pendiente de una persona u otro sistema.

## Avances

| Sesión | Avance esperado |
|---|---|
| 1 | Orientación, elección preliminar y preguntas. No hay entrega formal. |
| 2 | Ficha del caso, recorrido, contratos API y primera clasificación. |
| 3 | Conversación, fuente de datos, operación conectada y controles de autorización o confirmación. |
| 4 | Lote reanudable, magnitud clasificada y manejo de repeticiones y fallos. |
| 5 | Cinco casos, capturas reales, DeepEval y candidato de contenedor. |
| 6 | Demostración en GCP con persistencia y traza; explicación de límites y costos. |

La entrega final cierra el **domingo siguiente a la sesión 6 a las 23:59, hora de Lima**. La demostración de la sesión 6 permite recibir observaciones; incorpóralas antes del cierre.

## GCP

La evidencia de despliegue en GCP es parte del proyecto. Debe mostrar una revisión o imagen identificable, URL o endpoint operativo, persistencia y una operación completa. No publiques identificadores privados, credenciales ni capturas de secretos.

No necesitas comprar un plan personal. Si no tienes una cuenta habilitada, coordina con anticipación una ejecución en el entorno guiado por el docente y conserva evidencia de tu propia aplicación.

## Entregables

- repositorio con historial comprensible y `README.md` de ejecución;
- `.env.example` sin valores secretos;
- imagen de contenedor construible con `Dockerfile` y evidencia de su ejecución;
- datos o fixtures suficientes para repetir la demostración;
- cinco o más casos, capturas reales e informes de evaluación;
- evidencia de GCP y Langfuse sin secretos;
- [plantilla del proyecto](PLANTILLA-PROYECTO.md) completada.

El repositorio debe poder instalarse desde una copia limpia. No entregues `.env`, entornos virtuales, caches, tokens ni datos personales innecesarios.

## Rúbrica del proyecto

La siguiente rúbrica suma 100 puntos dentro del proyecto, equivalentes al 40% del curso.

| Componente | Puntos | Evidencia principal |
|---|---:|---|
| Caso, recorrido, contratos y límites | 15 | Problema concreto, entradas, salidas, errores y responsabilidades. |
| API y uso del LLM | 20 | Servicio ejecutable, salida validada, manejo del proveedor y consumo acotado. |
| Conversación, datos y operación conectada | 20 | Historial acotado, consultas reales y escritura o acción con control explícito. |
| Automatización y clasificación justificada | 15 | Lote reanudable, repeticiones seguras, sentimiento u otra magnitud pertinente. |
| Validación y evaluación | 15 | Cinco casos diversos, controles negativos, capturas reales y DeepEval; herramientas cuando aplique. |
| Observabilidad y GCP | 10 | Traza útil, contenedor, despliegue, persistencia y verificación del recorrido. |
| Claridad de entrega y demostración | 5 | README reproducible, evidencia legible y explicación de decisiones y límites. |

Una captura conceptual no demuestra ejecución. Una prueba simulada puede comprobar lógica local, pero debe distinguirse de la evidencia del proveedor, Langfuse o GCP.
