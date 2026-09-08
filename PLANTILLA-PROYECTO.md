# Plantilla del proyecto

## Identificación

- Estudiante:
- Nombre del proyecto:
- Caso o sector:
- Usuario principal:
- Problema que resolverá:

## Recorrido principal

Describe en cinco a ocho pasos qué inicia el usuario, qué consulta la aplicación, cuándo interviene el LLM, qué operación puede ejecutarse y qué resultado recibe.

1.
2.
3.
4.
5.

### Límites

- La aplicación sí puede:
- La aplicación no puede:
- Decisiones que conserva una persona u otro sistema:

## Contratos y seguridad

| Elemento | Decisión |
|---|---|
| Entrada principal | |
| Salida principal | |
| Errores esperados | |
| Identidad o alcance del usuario | |
| Operaciones de lectura | |
| Escrituras o acciones sensibles | |
| Confirmación o autorización requerida | |
| Comportamiento ante repetición | |

No uses un identificador escrito por el usuario como única prueba de identidad o permiso.

## Arquitectura

- API y contratos:
- Modelo y proveedor:
- Fuente de datos o sistema conectado:
- Herramientas:
- Persistencia:
- Procesamiento por lote:
- Observabilidad:
- GCP:

Incluye un diagrama pequeño que muestre usuario, API, LLM, herramientas, datos y confirmaciones.

## Clasificación

- Magnitud elegida: sentimiento / otra:
- Por qué ayuda al proceso:
- Etiquetas o escala:
- Evidencia que debe devolver:
- Decisiones que **no** autoriza esta clasificación:

## Avances

| Sesión | Resultado propio | Evidencia | Pendiente |
|---|---|---|---|
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |
| 6 | | | |

## Casos de validación

Incluye al menos cinco casos. Agrega filas si las necesitas.

| ID | Entrada | Resultado esperado | Herramientas esperadas | Tipo |
|---|---|---|---|---|
| 1 | | | | funcionamiento |
| 2 | | | | dato faltante |
| 3 | | | | seguridad |
| 4 | | | | error |
| 5 | | | | repetición o idempotencia |

### Resultados

- Ruta de las capturas reales:
- Ruta del informe determinista:
- Resultado del juez opcional y modelo usado:
- Fallos encontrados y correcciones:
- Límites que siguen abiertos:

## Despliegue y observabilidad

- Servicio y región de GCP:
- Revisión o imagen desplegada:
- Endpoint verificado:
- Mecanismo de persistencia:
- Recorrido comprobado:
- `trace_id` o evidencia Langfuse:
- Costo aproximado observado:
- Acción de cierre o control de gasto:

No pegues claves, tokens, contenido de `.env` ni identificadores privados innecesarios.

## Entrega final

- [ ] El repositorio incluye un `README.md` con instalación, configuración y demostración.
- [ ] `.env.example` contiene solo nombres y valores de ejemplo.
- [ ] `.gitignore` excluye secretos, entorno, caches y salidas temporales.
- [ ] El `Dockerfile` construye una imagen de la aplicación.
- [ ] Guardé evidencia del comando, etiqueta y ejecución de la imagen de contenedor.
- [ ] Los contratos y errores están documentados.
- [ ] Las operaciones sensibles tienen autorización o confirmación explícita.
- [ ] El lote se puede reanudar sin duplicar trabajo terminado.
- [ ] Hay al menos cinco casos diversos y capturas del sistema real.
- [ ] DeepEval usa las herramientas realmente observadas cuando corresponde.
- [ ] La evidencia muestra Langfuse y una ejecución en GCP.
- [ ] Cada captura fue revisada y no expone secretos.
- [ ] La demostración explica qué está implementado y qué permanece fuera de alcance.
