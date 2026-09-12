# Laboratorios · Construcción de Aplicaciones Impulsadas por IA

Cada laboratorio es una aplicación completa e independiente. Contiene el código de las semanas anteriores más lo que corresponde a esa sesión. Puedes empezar directamente por cualquiera y volver a probar otra semana sin modificarla.

| Carpeta | Sesión del curso | Aplicación incluida |
|---|---:|---|
| [lab-01](lab-01/README.md) | 2 | API de clasificación, contratos y autenticación. |
| [lab-02](lab-02/README.md) | 3 | Todo lo anterior + chatbot, herramientas, CRM y confirmación. |
| [lab-03](lab-03/README.md) | 4 | Todo lo anterior + lote reanudable y análisis TXT. |
| [lab-04](lab-04/README.md) | 5 | Todo lo anterior + capturas, DeepEval y contenedor local. |
| [lab-05](lab-05/README.md) | 6 | Todo lo anterior + Cloud Run, GCS, secretos y Langfuse. |

La sesión 1 presenta fundamentos y diseño; no tiene laboratorio de código.

## Empezar por una semana

```bash
git clone https://github.com/jucarBM/construccion-aplicaciones-ia.git
cd construccion-aplicaciones-ia/lab-02
```

Sigue el `README.md` de esa carpeta para crear su entorno, configurar `.env`, ejecutar pruebas y abrir la API. No necesitas completar LAB-01 ni copiar sus cambios. La aplicación ya está terminada hasta la semana elegida: los ejercicios proponen ejecutarla y experimentar en Swagger con las entradas.

Cada carpeta tiene su propio `servicio/`, dependencias, datos cuando corresponden, pruebas e instrucciones de esa sesión. No usa enlaces simbólicos ni imports entre laboratorios. Los entornos, claves y resultados quedan separados. Detén el servidor de una semana antes de arrancar otra en el mismo puerto.

## Proyecto personal

[Proyecto del curso](PROYECTO.md) · [Plantilla](PLANTILLA-PROYECTO.md). Estos documentos comunes se mantienen una sola vez en la raíz.

El proyecto personal tiene sus propios avances; los laboratorios son versiones completas de referencia. Cada estudiante conserva evidencia de su ejecución. Las pruebas controladas no consumen el LLM; las llamadas reales y los servicios externos requieren sus credenciales.

[Contexto común del caso](docs/CASO.md) · [Guía oficial de Responses](https://developers.openai.com/api/docs/guides/migrate-to-responses)
