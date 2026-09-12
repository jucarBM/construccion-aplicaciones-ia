# LAB-05 · Despliegue y trazas

Sesión 6. Código completo hasta esta semana. Se ejecuta desde esta carpeta, sin importar código de otro laboratorio.

## Preparación

Desde la raíz del repositorio:

```bash
cd lab-05
uv venv .venv --python 3.12
```

Activa el entorno y crea tu configuración **solo la primera vez**:

```bash
# macOS / Linux
source .venv/bin/activate
cp .env.example .env
```

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
```

Edita `.env`: completa `OPENAI_API_KEY` y cambia `API_KEY`. El ejemplo usa OpenAI Responses y `gpt-4o-mini`. `OPENAI_BASE_URL` y `OPENAI_MODEL` permiten otro proveedor que implemente Responses, herramientas y salida estructurada. Una clave de otro proveedor no funciona contra OpenAI.

```bash
uv pip install -r requirements.txt
uv pip install -r requirements-evaluacion.txt
uv pip install -r requirements-despliegue.txt
python -m pytest -q
```

Las pruebas son locales y no consumen el LLM. Para la API:

```bash
python -m uvicorn servicio.main:app --reload --port 8000
```

Abre [Swagger](http://127.0.0.1:8000/docs). Detén el servidor anterior antes de cambiar de lab. En cada operación protegida, pulsa **Try it out**, introduce tu `X-API-Key`, pega el JSON y pulsa **Execute**.


**Organización:** prepara proyecto, identidades y secretos antes de clase; reserva el bloque de laboratorio para construir, desplegar y comprobar. El recorrido completo de abajo estima 90 minutos, incluida la preparación.

**Resultado:** una revisión privada de Cloud Run ejecuta el mismo contenedor del laboratorio, usa GCS para los registros generados y supera un recorrido externo con autenticación de Google Cloud y `X-API-Key`.

Este laboratorio trabaja en un **proyecto temporal y dedicado**. El docente entrega el identificador del proyecto con facturación habilitada. No uses un proyecto compartido ni uno que contenga otros recursos.

Esta carpeta contiene también API, chatbot, lote y evaluación completos. Puedes ejecutar primero la [preparación local](#preparación) sin abrir otro laboratorio.

## Qué se despliega

La imagen contiene un proceso `uvicorn`, `servicio/`, las dependencias y dos archivos de referencia: `crm/pedidos.txt` y `crm/politicas.txt`. La aplicación lee esos dos TXT desde la imagen. Cada estudiante conserva evidencia de su propia ejecución.

Cuando `CRM_BUCKET` está definido, GCS se usa para:

- crear `solicitudes/SOL-….txt` y `analisis/ANA-….txt` sin reemplazar objetos existentes;
- leer una solicitud ya creada por `GET /api/solicitudes/{solicitud_id}`.

El LLM y Langfuse son servicios externos. Secret Manager entrega las claves a Cloud Run. No se copia `.env` dentro de la imagen.

## Cronograma

| Minutos | Actividad |
|---:|---|
| 0–10 | Verificar proyecto, cuenta y variables |
| 10–25 | Crear repositorio, buckets e identidades |
| 25–35 | Cargar secretos sin mostrarlos |
| 35–50 | Preparar contexto seguro y construir la imagen |
| 50–65 | Desplegar una revisión privada de Cloud Run |
| 65–85 | Probar salud, 401, propuesta, confirmación, lectura y repetición |
| 85–90 | Guardar evidencia y revisar limpieza |

La creación del proyecto y la asociación de la cuenta de facturación quedan preconfiguradas por el docente. Cloud Build, Artifact Registry, Cloud Run, Secret Manager, GCS, el proveedor LLM y Langfuse pueden generar cargos; no se presume costo cero.

## 1. Abrir Cloud Shell y fijar el alcance

Usa **Google Cloud Shell** también si trabajas desde Windows. Los comandos siguientes suponen Bash, `gcloud`, `curl` y `jq`.

Sustituye únicamente `tu-proyecto-dedicado` por el proyecto asignado:

```bash
export PROJECT_ID="tu-proyecto-dedicado"
export REGION="us-central1"
export REPOSITORY="curso-ia"
export SERVICE="tienda-ia"
export RUNTIME_SA="curso-app"
export BUILD_SA="curso-build"
export RECORDS_BUCKET="${PROJECT_ID}-tienda-ia-registros"
export BUILD_BUCKET="${PROJECT_ID}_cloudbuild"
export IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE}:v1"
export RUNTIME_SA_EMAIL="${RUNTIME_SA}@${PROJECT_ID}.iam.gserviceaccount.com"
export BUILD_SA_EMAIL="${BUILD_SA}@${PROJECT_ID}.iam.gserviceaccount.com"
```

Comprueba el proyecto antes de crear recursos:

```bash
gcloud config set project "$PROJECT_ID"
gcloud projects describe "$PROJECT_ID" --format='value(projectId,name)'
gcloud billing projects describe "$PROJECT_ID" --format='value(billingEnabled)'
```

Continúa solo si el identificador es el proyecto temporal asignado y `billingEnabled` muestra `True`.

Habilita las APIs necesarias:

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  iam.googleapis.com \
  storage.googleapis.com
```

## 2. Crear almacenamiento, repositorio e identidades

```bash
gcloud artifacts repositories create "$REPOSITORY" \
  --repository-format=docker \
  --location="$REGION" \
  --description="Imágenes del curso"

gcloud storage buckets create "gs://${RECORDS_BUCKET}" \
  --location="$REGION" \
  --uniform-bucket-level-access \
  --public-access-prevention

gcloud storage buckets create "gs://${BUILD_BUCKET}" \
  --location="$REGION" \
  --uniform-bucket-level-access \
  --public-access-prevention

gcloud iam service-accounts create "$RUNTIME_SA" \
  --display-name="Aplicación del curso"

gcloud iam service-accounts create "$BUILD_SA" \
  --display-name="Compilación del curso"
```

La identidad de ejecución solo necesita operar objetos dentro del bucket de registros:

```bash
gcloud storage buckets add-iam-policy-binding "gs://${RECORDS_BUCKET}" \
  --member="serviceAccount:${RUNTIME_SA_EMAIL}" \
  --role="roles/storage.objectUser"
```

La identidad de compilación recibe tres permisos acotados. No necesita `Editor`:

```bash
gcloud storage buckets add-iam-policy-binding "gs://${BUILD_BUCKET}" \
  --member="serviceAccount:${BUILD_SA_EMAIL}" \
  --role="roles/storage.objectViewer"

gcloud artifacts repositories add-iam-policy-binding "$REPOSITORY" \
  --location="$REGION" \
  --member="serviceAccount:${BUILD_SA_EMAIL}" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${BUILD_SA_EMAIL}" \
  --role="roles/logging.logWriter" \
  --condition=None
```

Autoriza a la cuenta activa a usar esa identidad solo para la compilación:

```bash
export ACTIVE_ACCOUNT="$(gcloud config get-value account)"
gcloud iam service-accounts add-iam-policy-binding "$BUILD_SA_EMAIL" \
  --member="user:${ACTIVE_ACCOUNT}" \
  --role="roles/iam.serviceAccountUser"

gcloud iam service-accounts add-iam-policy-binding "$RUNTIME_SA_EMAIL" \
  --member="user:${ACTIVE_ACCOUNT}" \
  --role="roles/iam.serviceAccountUser"
```

## 3. Crear secretos sin escribir valores en el historial

Los nombres de las variables ordinarias sí pueden aparecer en comandos. Los valores de `API_KEY`, `PROPUESTA_SECRET`, `OPENAI_API_KEY` y las claves de Langfuse para la verificación final van a Secret Manager.

Crea una carpeta privada temporal y genera las dos claves internas:

```bash
umask 077
export PRIVATE_DIR="$(mktemp -d)"
printf '%s' "$(openssl rand -hex 32)" > "${PRIVATE_DIR}/api_key"
printf '%s' "$(openssl rand -hex 32)" > "${PRIVATE_DIR}/propuesta_secret"
read -r -s -p "OPENAI_API_KEY: " OPENAI_VALUE; printf '\n'
printf '%s' "$OPENAI_VALUE" > "${PRIVATE_DIR}/openai_api_key"
unset OPENAI_VALUE
```

Crea cada secreto una sola vez. En este proyecto nuevo, el valor cargado queda en la versión `1`:

```bash
gcloud secrets create "${SERVICE}-api-key" \
  --replication-policy=automatic \
  --data-file="${PRIVATE_DIR}/api_key"

gcloud secrets create "${SERVICE}-propuesta-secret" \
  --replication-policy=automatic \
  --data-file="${PRIVATE_DIR}/propuesta_secret"

gcloud secrets create "${SERVICE}-openai-api-key" \
  --replication-policy=automatic \
  --data-file="${PRIVATE_DIR}/openai_api_key"
```

Da acceso a la identidad de ejecución en cada secreto, sin conceder acceso a todos los secretos del proyecto:

```bash
for SECRET_NAME in \
  "${SERVICE}-api-key" \
  "${SERVICE}-propuesta-secret" \
  "${SERVICE}-openai-api-key"
do
  gcloud secrets add-iam-policy-binding "$SECRET_NAME" \
    --member="serviceAccount:${RUNTIME_SA_EMAIL}" \
    --role="roles/secretmanager.secretAccessor"
done
```

### Langfuse en la evidencia final

Puedes probar el arranque y la persistencia con Langfuse apagado para aislar fallos. La evidencia final de S6 sí requiere una traza. Si el docente entregó un proyecto de Langfuse, captura sus claves de la misma forma:

```bash
read -r -s -p "LANGFUSE_PUBLIC_KEY: " LF_PUBLIC; printf '\n'
printf '%s' "$LF_PUBLIC" > "${PRIVATE_DIR}/langfuse_public_key"
unset LF_PUBLIC
read -r -s -p "LANGFUSE_SECRET_KEY: " LF_SECRET; printf '\n'
printf '%s' "$LF_SECRET" > "${PRIVATE_DIR}/langfuse_secret_key"
unset LF_SECRET

gcloud secrets create "${SERVICE}-langfuse-public-key" \
  --replication-policy=automatic \
  --data-file="${PRIVATE_DIR}/langfuse_public_key"
gcloud secrets create "${SERVICE}-langfuse-secret-key" \
  --replication-policy=automatic \
  --data-file="${PRIVATE_DIR}/langfuse_secret_key"

for SECRET_NAME in \
  "${SERVICE}-langfuse-public-key" \
  "${SERVICE}-langfuse-secret-key"
do
  gcloud secrets add-iam-policy-binding "$SECRET_NAME" \
    --member="serviceAccount:${RUNTIME_SA_EMAIL}" \
    --role="roles/secretmanager.secretAccessor"
done
```

## 4. Construir desde un contexto seguro

Ubícate en `lab-05/` del repositorio descargado. Todo el contexto de esta práctica está dentro de esa carpeta. Prepara una carpeta que contenga únicamente los archivos requeridos por el `Dockerfile`:

```bash
export BUILD_DIR="$(mktemp -d)"
export BUILD_CONFIG="$(mktemp)"
cp Dockerfile requirements.txt requirements-despliegue.txt "$BUILD_DIR/"
cp -R servicio "$BUILD_DIR/servicio"
mkdir "$BUILD_DIR/crm"
cp crm/pedidos.txt crm/politicas.txt "$BUILD_DIR/crm/"
find "$BUILD_DIR" -type f -print | sort
```

La lista debe contener solo:

```text
Dockerfile
requirements.txt
requirements-despliegue.txt
servicio/...
crm/pedidos.txt
crm/politicas.txt
```

No debe aparecer `.env`, `crm/solicitudes/`, `crm/analisis/`, `tests/`, capturas ni informes.

Prueba primero el mismo contexto en Docker. Este control solo verifica que la imagen arranca; no consume el LLM:

```bash
docker build -t tienda-ia:local "$BUILD_DIR"
docker run --rm -d \
  --name tienda-ia-local \
  -p 8080:8080 \
  tienda-ia:local
curl -fsS "http://127.0.0.1:8080/salud" | jq
curl -fsS -o /dev/null -w '%{http_code}\n' \
  "http://127.0.0.1:8080/docs"
docker stop tienda-ia-local
```

Los resultados esperados son `{"estado":"ok"}` y `200`. Si Cloud Shell informa que Docker no está disponible, conserva ese bloqueo y continúa con Cloud Build; no presentes la compilación remota como prueba local.

La cuenta de compilación escribe logs en Cloud Logging. Guarda la configuración fuera del contexto de origen para que tampoco viaje dentro de la imagen:

```bash
cat > "$BUILD_CONFIG" <<'YAML'
steps:
- name: gcr.io/cloud-builders/docker
  args: [build, -t, '${_IMAGE}', .]
images: ['${_IMAGE}']
options:
  logging: CLOUD_LOGGING_ONLY
YAML
```

Envía ese contexto a Cloud Build con la identidad acotada y el bucket de staging explícito:

```bash
gcloud builds submit "$BUILD_DIR" \
  --region="$REGION" \
  --config="$BUILD_CONFIG" \
  --substitutions="_IMAGE=${IMAGE}" \
  --service-account="projects/${PROJECT_ID}/serviceAccounts/${BUILD_SA_EMAIL}" \
  --gcs-source-staging-dir="gs://${BUILD_BUCKET}/source"
```

Conserva el identificador final del build y comprueba que la imagen existe:

```bash
gcloud artifacts docker images describe "$IMAGE" \
  --format='value(image_summary.digest)'
```

### Alternativa con `.gcloudignore`

Si no puedes usar una carpeta temporal, guarda este `.gcloudignore` dentro de `lab-05/`:

```gitignore
*
!Dockerfile
!requirements.txt
!requirements-despliegue.txt
!servicio/
!servicio/**
!crm/
!crm/pedidos.txt
!crm/politicas.txt
```

Inspecciona la lista antes de subir y señala el archivo de exclusión de forma explícita:

```bash
gcloud meta list-files-for-upload .
cat > "$BUILD_CONFIG" <<'YAML'
steps:
- name: gcr.io/cloud-builders/docker
  args: [build, -t, '${_IMAGE}', .]
images: ['${_IMAGE}']
options:
  logging: CLOUD_LOGGING_ONLY
YAML
gcloud builds submit . \
  --ignore-file=.gcloudignore \
  --region="$REGION" \
  --config="$BUILD_CONFIG" \
  --substitutions="_IMAGE=${IMAGE}" \
  --service-account="projects/${PROJECT_ID}/serviceAccounts/${BUILD_SA_EMAIL}" \
  --gcs-source-staging-dir="gs://${BUILD_BUCKET}/source"
```

## 5. Desplegar una revisión privada

La ruta principal mantiene Cloud Run privado. Cada petición necesita identidad de Google Cloud; las rutas `/api/*` exigen además `X-API-Key` dentro de FastAPI.

```bash
gcloud run deploy "$SERVICE" \
  --image="$IMAGE" \
  --region="$REGION" \
  --platform=managed \
  --service-account="$RUNTIME_SA_EMAIL" \
  --no-allow-unauthenticated \
  --min-instances=0 \
  --max-instances=1 \
  --cpu=1 \
  --memory=512Mi \
  --concurrency=1 \
  --set-env-vars="OPENAI_BASE_URL=https://api.openai.com/v1,OPENAI_MODEL=gpt-4o-mini,CLIENTE_DEMO=C-001,FECHA_ESCENARIO=2026-09-08,CRM_BUCKET=${RECORDS_BUCKET},LANGFUSE_ENABLED=false,LANGFUSE_BASE_URL=https://cloud.langfuse.com" \
  --set-secrets="API_KEY=${SERVICE}-api-key:1,PROPUESTA_SECRET=${SERVICE}-propuesta-secret:1,OPENAI_API_KEY=${SERVICE}-openai-api-key:1"
```

`OPENAI_BASE_URL` y `OPENAI_MODEL` son configuración ordinaria. Cámbialos juntos si el docente indicó otro proveedor compatible.

Para activar Langfuse después de crear sus dos secretos:

```bash
gcloud run services update "$SERVICE" \
  --region="$REGION" \
  --update-env-vars="LANGFUSE_ENABLED=true,LANGFUSE_BASE_URL=https://cloud.langfuse.com" \
  --update-secrets="LANGFUSE_PUBLIC_KEY=${SERVICE}-langfuse-public-key:1,LANGFUSE_SECRET_KEY=${SERVICE}-langfuse-secret-key:1"
```

Ejecuta esta actualización antes de capturar la evidencia final. Si todavía no tienes credenciales de Langfuse, registra el bloqueo y coordina una ejecución guiada con el docente; el bloqueo no sustituye la traza requerida.

No desactives la comprobación de IAM para sortear una política de la organización. Un servicio público solo es una alternativa si el propietario del proyecto y la política institucional lo permiten de forma explícita.

## 6. Probar las dos capas de autenticación

Obtén la revisión, imagen y URL que Cloud Run reporta:

```bash
gcloud run services describe "$SERVICE" \
  --region="$REGION" \
  --format='yaml(status.url,status.latestReadyRevisionName,status.traffic,spec.template.spec.containers[0].image)'
```

En una primera pestaña de Cloud Shell, abre un proxy autenticado:

```bash
gcloud run services proxy "$SERVICE" \
  --region="$REGION" \
  --port=8080
```

Mantén esa pestaña abierta. El proxy usa tu identidad de Google Cloud. En una segunda pestaña:

```bash
export SERVICE_URL="http://127.0.0.1:8080"
{
  printf 'X-API-Key: '
  cat "${PRIVATE_DIR}/api_key"
  printf '\n'
} > "${PRIVATE_DIR}/api_header"
curl -fsS "${SERVICE_URL}/salud" | jq
curl -sS -o /dev/null -w '%{http_code}\n' \
  "${SERVICE_URL}/api/pedidos/P-1042"
curl -fsS -H @"${PRIVATE_DIR}/api_header" \
  "${SERVICE_URL}/api/pedidos/P-1042" | jq
```

Resultados esperados:

- `/salud` devuelve `{"estado":"ok"}`;
- la ruta `/api/pedidos/P-1042` sin `X-API-Key` devuelve `401`;
- la misma ruta con la clave devuelve el pedido `P-1042` del cliente fijo `C-001`.

En el navegador de Cloud Shell puedes abrir `http://127.0.0.1:8080/docs` mediante la vista previa del puerto 8080.

## 7. Probar propuesta, confirmación, lectura y repetición

La primera llamada entrega una **propuesta**, no una devolución aprobada. El servidor firma `pedido_id` y `motivo` para `C-001`.

```bash
export MOTIVO="Llegó otro modelo"
export PROPOSAL_JSON="$(mktemp)"

curl -fsS -X POST "${SERVICE_URL}/api/chat" \
  -H @"${PRIVATE_DIR}/api_header" \
  -H 'Content-Type: application/json' \
  -d "$(jq -n \
    --arg mensaje 'Quiero solicitar una devolución' \
    --arg pedido_id 'P-1042' \
    --arg motivo "$MOTIVO" \
    '{mensaje:$mensaje,pedido_id:$pedido_id,motivo:$motivo}')" \
  -o "$PROPOSAL_JSON"

jq '{respuesta,herramientas,propuesta,solicitud_id,trace_id}' "$PROPOSAL_JSON"
export PROPOSAL_TOKEN="$(jq -er '.propuesta.propuesta_token' "$PROPOSAL_JSON")"
```

La confirmación HTTP debe devolver exactamente el mismo `pedido_id`, el mismo `motivo` y el token emitido:

```bash
export CONFIRM_JSON="$(mktemp)"
jq -n \
  --arg mensaje 'Confirmo la solicitud para revisión' \
  --arg pedido_id 'P-1042' \
  --arg motivo "$MOTIVO" \
  --arg token "$PROPOSAL_TOKEN" \
  '{mensaje:$mensaje,pedido_id:$pedido_id,motivo:$motivo,
    confirmacion:{acepta:true,pedido_id:$pedido_id,motivo:$motivo,propuesta_token:$token}}' \
  > "$CONFIRM_JSON"

export FIRST_JSON="$(mktemp)"
curl -fsS -X POST "${SERVICE_URL}/api/chat" \
  -H @"${PRIVATE_DIR}/api_header" \
  -H 'Content-Type: application/json' \
  --data-binary "@${CONFIRM_JSON}" \
  -o "$FIRST_JSON"

jq '{respuesta,solicitud_id,registro:.herramientas[0].resultado}' "$FIRST_JSON"
export SOL_ID="$(jq -er '.solicitud_id' "$FIRST_JSON")"
```

El primer registro esperado tiene `creada: true` y estado `recibida_para_revision`. Crear la solicitud no aprueba la devolución ni ejecuta un reembolso.

Lee el TXT mediante la API y comprueba el objeto en GCS:

```bash
curl -fsS -H @"${PRIVATE_DIR}/api_header" \
  "${SERVICE_URL}/api/solicitudes/${SOL_ID}" | jq

gcloud storage ls "gs://${RECORDS_BUCKET}/solicitudes/"
gcloud storage cat "gs://${RECORDS_BUCKET}/solicitudes/${SOL_ID}.txt"
```

Repite exactamente la misma confirmación:

```bash
export REPEAT_JSON="$(mktemp)"
curl -fsS -X POST "${SERVICE_URL}/api/chat" \
  -H @"${PRIVATE_DIR}/api_header" \
  -H 'Content-Type: application/json' \
  --data-binary "@${CONFIRM_JSON}" \
  -o "$REPEAT_JSON"

jq '{solicitud_id,registro:.herramientas[0].resultado}' "$REPEAT_JSON"
test "$(jq -r '.solicitud_id' "$FIRST_JSON")" = \
     "$(jq -r '.solicitud_id' "$REPEAT_JSON")"
```

La segunda respuesta debe conservar el mismo `SOL_ID` y mostrar `creada: false`. `if_generation_match=0` evita reemplazar el objeto original.

## 8. Guardar evidencia

Antes de declarar el laboratorio completado, conserva:

- identificador exitoso de Cloud Build y digest de la imagen;
- nombre de la revisión lista y porcentaje de tráfico;
- respuesta de `/salud`;
- `401` sin `X-API-Key` a través del proxy autenticado;
- pedido obtenido con la clave;
- propuesta sin `solicitud_id`;
- primera confirmación con `creada: true`;
- lectura del `SOL` desde la API y GCS;
- repetición con el mismo `SOL_ID` y `creada: false`;
- `trace_id` y la traza correspondiente visible en Langfuse;
- logs del servicio sin valores secretos.

Consulta revisiones y logs:

```bash
gcloud run revisions list \
  --service="$SERVICE" \
  --region="$REGION"

gcloud run services logs read "$SERVICE" \
  --region="$REGION" \
  --limit=50
```

Marca como **bloqueo** cualquier paso que no tenga evidencia. Una compilación correcta no demuestra por sí sola autenticación, persistencia ni trazas.

## 9. Limpiar el entorno

Detén primero el proxy con `Ctrl+C`. Elimina archivos temporales y variables locales:

```bash
unset PROPOSAL_TOKEN MOTIVO SOL_ID
rm -f -- "$PROPOSAL_JSON" "$CONFIRM_JSON" "$FIRST_JSON" "$REPEAT_JSON"
rm -f -- "$BUILD_CONFIG"
if [ -n "${PRIVATE_DIR:-}" ] && [ -d "$PRIVATE_DIR" ]; then
  rm -rf -- "$PRIVATE_DIR"
fi
if [ -n "${BUILD_DIR:-}" ] && [ -d "$BUILD_DIR" ]; then
  rm -rf -- "$BUILD_DIR"
fi
```

Si necesitas retirar solo la aplicación y conservar el proyecto para revisar evidencia:

```bash
gcloud run services delete "$SERVICE" \
  --region="$REGION" \
  --quiet
```

Al terminar la revisión docente, elimina el proyecto **solo si sigue siendo el proyecto temporal dedicado**:

```bash
export CURRENT_PROJECT="$(gcloud config get-value project)"
if [ "$CURRENT_PROJECT" = "$PROJECT_ID" ]; then
  gcloud projects delete "$PROJECT_ID"
else
  printf 'No se elimina: el proyecto activo no coincide con PROJECT_ID.\n' >&2
fi
```

La eliminación del servicio o del proyecto no cancela cargos ya generados en proveedores externos. Revisa también los recursos del proveedor LLM y de Langfuse usados durante la práctica.

## Entregable

Entrega una página con:

1. proyecto, región, servicio, revisión e imagen, sin claves;
2. diagrama de un contenedor con LLM, Langfuse y GCS externos;
3. tabla de verificaciones con resultado y enlace a evidencia;
4. el mismo `SOL_ID` en la primera confirmación, lectura y repetición;
5. costos o consumo disponibles, o `no disponible` con su condición de medición;
6. bloqueos pendientes y la acción concreta para resolverlos.


[Proyecto del curso](../PROYECTO.md) · [Plantilla de entrega](../PLANTILLA-PROYECTO.md)
