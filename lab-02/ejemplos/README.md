# Una conversación en Swagger: el pedido P-1042

La cliente recibió audífonos blancos. Quiere comprobar su compra, reportar la diferencia y dejar una solicitud para revisión. El CRM registra **Audífonos negros**. Usaremos el mismo pedido durante toda la conversación.

## Abre el chatbot

1. Inicia FastAPI siguiendo el [README del laboratorio](../README.md).
2. Abre [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
3. Despliega **POST /api/chat** y pulsa **Try it out**.
4. En `X-API-Key`, escribe el valor de tu `.env`.
5. Sustituye todo el **Request body** por un ejemplo de abajo y pulsa **Execute**.
6. Lee **Response body**. Para el siguiente turno, reemplaza el cuerpo de la petición y vuelve a ejecutar.

Las peticiones conversacionales llaman al proveedor configurado. Un `401` significa que debes revisar `X-API-Key`; un `422`, los campos del cuerpo; un `503`, la configuración o respuesta del proveedor. El detalle del error aparece en la respuesta.

## 1. Consulta qué producto compró

Copia este cuerpo completo:

```json
{
  "mensaje": "¿Qué producto figura en mi pedido P-1042?",
  "pedido_id": "P-1042"
}
```

**Mira la respuesta:** `respuesta` debería indicar Audífonos negros. En `herramientas`, busca `consultar_pedido` y abre su `resultado`: debe corresponder a P-1042 y C-001. `propuesta` y `solicitud_id` son `null` porque solo estamos consultando.

La redacción del modelo puede variar. Si responde sin consultar, no supongas que leyó el CRM: comprueba la herramienta observada.

**Prueba un cambio:** sustituye P-1042 por P-2099 tanto en el mensaje como en el campo. Pertenece a otro cliente; la herramienta debe devolver `pedido_no_encontrado`, sin mostrar sus datos. Después vuelve a P-1042.

## 2. Continúa la conversación con historial

Copia este ejemplo. En el turno `asistente`, puedes pegar la respuesta real que obtuviste en el paso 1:

```json
{
  "mensaje": "¿Y cuándo se entregó?",
  "historial": [
    {
      "rol": "usuario",
      "contenido": "¿Qué producto figura en mi pedido P-1042?"
    },
    {
      "rol": "asistente",
      "contenido": "El producto registrado es Audífonos negros."
    }
  ]
}
```

**Mira la respuesta:** el historial contiene P-1042 y permite entender a qué pedido se refiere «se entregó». El CRM indica el **4 de septiembre de 2026**. Revisa si el modelo volvió a consultar el dato.

**Ahora quita el contexto:** envía este cuerpo completo:

```json
{
  "mensaje": "¿Y cuándo se entregó?"
}
```

El chatbot debería pedir la referencia del pedido. FastAPI no guarda una conversación entre peticiones: lo que no reenvías no forma parte del contexto actual. El contrato acepta hasta 12 mensajes de historial y la aplicación envía los últimos 8.

## 3. Reporta que llegó otro producto

```json
{
  "mensaje": "Me llegaron audífonos blancos. Quiero reportarlo.",
  "pedido_id": "P-1042",
  "motivo": "Recibí un producto distinto"
}
```

**Mira la respuesta:** debe aparecer `propuesta`, con pedido, motivo, acción y `propuesta_token`. Las consultas de pedido y política llevan `origen: "aplicacion"`: aquí el código las inicia antes de pedir al modelo una explicación.

El caso fija el 8 de septiembre de 2026: transcurrieron cuatro días desde la entrega, dentro del plazo de 30 días. La propuesta permite abrir una solicitud para revisión. **Todavía no se registra.**

**Prueba un cambio:** envía el mismo cuerpo con `"mensaje": "Sí, confirmo"`, pero sin añadir el objeto `confirmacion`. El texto por sí solo no autoriza la escritura.

## 4. Confirma la propuesta

Copia el cuerpo y sustituye `PEGA_EL_TOKEN_DE_LA_PROPUESTA` por el valor recibido en el paso 3. Conserva exactamente el mismo pedido y motivo:

```json
{
  "mensaje": "Confirmo la propuesta.",
  "pedido_id": "P-1042",
  "motivo": "Recibí un producto distinto",
  "confirmacion": {
    "acepta": true,
    "pedido_id": "P-1042",
    "motivo": "Recibí un producto distinto",
    "propuesta_token": "PEGA_EL_TOKEN_DE_LA_PROPUESTA"
  }
}
```

**Mira la respuesta:** `solicitud_id` contiene un SOL. En `herramientas[0].resultado`, revisa `creada` y `estado: "recibida_para_revision"`. Esta confirmación la procesa la aplicación sin volver a llamar al modelo.

En Swagger abre **GET /api/solicitudes/{solicitud_id}**, pulsa **Try it out**, pega el SOL y tu `X-API-Key`, y ejecuta. También puedes leer el TXT en `crm/solicitudes/`.

Registrar no aprueba la devolución ni ejecuta un reembolso. El equipo de atención debe resolver la solicitud después.

## 5. Repite y cambia un dato

- **Repite exactamente la confirmación:** debe devolver el mismo SOL y `creada: false`. No aparece otro archivo.
- **Cambia solo `confirmacion.motivo`:** debe responder `422`, porque no coincide con el motivo del cuerpo principal.
- **Restaura el motivo y altera un carácter del token:** busca `confirmacion_http_valida_requerida` en el resultado de la herramienta. Puede aparecer con HTTP `200`; comprueba el cuerpo y que no haya un nuevo SOL.

Si el registro ya existía antes de empezar, la primera confirmación también puede indicar `creada: false`. Para practicar una solicitud nueva, usa otro motivo desde el paso 3 y confirma la nueva propuesta. No cambies únicamente la confirmación.

## Qué explicar al terminar

Muestra una petición, la herramienta que se ejecutó y el resultado. Después muestra la propuesta, la confirmación y el SOL. Explica qué hizo la cliente, qué decidió el modelo y qué validó la aplicación. Oculta claves y tokens al guardar capturas.
