# Caso de las prácticas: pedidos y devoluciones

Una persona recibió unos audífonos distintos de los que pidió. Escribe: «Me llegó otro producto. Mi pedido es P-1042». Construiremos una aplicación que consulte el pedido y la política de la tienda, explique el siguiente paso y registre una solicitud cuando el cliente confirme.

Los registros de la tienda son didácticos y están en `crm/`. Las llamadas al modelo, las consultas de archivos y las escrituras que ejecutamos sí son reales. Este caso guía los cinco laboratorios; tu proyecto puede resolver otro problema.

## Qué hace la aplicación

1. Recibe un mensaje y puede clasificar intención, sentimiento y urgencia, indicando una frase como evidencia.
2. Consulta el pedido del cliente de demostración `C-001` y la política de devolución.
3. Pide el número de pedido o el motivo cuando falten.
4. Devuelve una propuesta de solicitud con los datos que el cliente debe revisar.
5. Recibe una confirmación explícita de esa propuesta y guarda un TXT con un identificador `SOL-…`.
6. Si se repite la misma solicitud, devuelve el mismo identificador sin crear otro registro.

La solicitud queda **recibida para revisión**. El sistema no aprueba devoluciones ni ejecuta reembolsos. La aplicación comprueba que el pedido esté entregado y dentro del plazo de 30 días antes de proponer el trámite. Una persona revisa la solicitud y decide la resolución. La política orienta al cliente; el sentimiento de un mensaje no cambia sus derechos ni autoriza una operación.

## Quién decide cada cosa

| Componente | Responsabilidad |
|---|---|
| Cliente | Describe el problema, aporta el pedido y confirma los datos de la solicitud. |
| FastAPI y Pydantic | Reciben y validan la petición y protegen las rutas de la aplicación. |
| LLM | Clasifica texto, formula respuestas y puede solicitar herramientas de consulta. |
| Herramientas | Leen pedidos y políticas. La aplicación controla la escritura confirmada. |
| CRM TXT | Conserva los datos de ejemplo y los nuevos registros. En GCP, los registros nuevos se guardan en Cloud Storage. |

La clave de la API permite usar la aplicación. Este laboratorio tiene un único cliente de demostración configurado en el servidor. No implementa un sistema de cuentas de clientes.

## Por qué confirmar requiere más que escribir «sí»

La aplicación devuelve una propuesta firmada que vincula cliente, pedido y motivo. La siguiente petición debe devolver esos datos y la aceptación explícita. Cambiar el pedido o el motivo invalida la confirmación. La firma es un detalle del servicio: el alumno puede seguir el flujo sin implementar criptografía desde cero.

El historial de conversación y una instrucción del modelo nunca conceden permiso para escribir. La app revisa la confirmación antes de registrar.

## Casos que debemos demostrar

- Consultar un pedido que pertenece al cliente y explicar su estado con datos del TXT.
- Pedir el dato faltante cuando el mensaje no identifica el pedido.
- Rechazar la consulta de un pedido ajeno o inexistente sin revelar sus datos.
- Proponer una solicitud sin escribirla todavía.
- Registrar después de confirmar y recuperar su identificador.
- Repetir la confirmación sin duplicar el TXT.
- Rechazar una propuesta alterada.
- Clasificar mensajes de un lote y conservar cada resultado terminado.
- Distinguir una respuesta del modelo de un fallo del proveedor o de almacenamiento.

## Archivos y lectura recomendada

Empieza por `servicio/main.py` y `servicio/contratos.py`. Continúa con `servicio/llm.py` para localizar la llamada al modelo, `servicio/chat.py` para seguir la conversación y `servicio/herramientas.py` y `servicio/crm.py` para comprobar qué se lee o escribe. `servicio/lote.py` utiliza esa misma clasificación para procesar mensajes de una carpeta.
