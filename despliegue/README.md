# Desplegar en Cloud Run

Lo que hace falta antes de empezar: una cuenta de Google Cloud con facturación
habilitada. La prueba gratuita da 300 dólares por 90 días y pide una tarjeta,
aunque no cobra sola cuando el crédito se termina: hay que pasar a cuenta paga
a mano. Encima de eso, Cloud Run tiene dos millones de peticiones por mes
gratis para siempre, así que un servicio de curso no consume crédito real.

## Una vez, al principio

```bash
gcloud auth login
gcloud config set project SU-PROYECTO
gcloud services enable run.googleapis.com \
                       artifactregistry.googleapis.com \
                       secretmanager.googleapis.com
```

## Las claves no viajan en el contenedor

La clave no va en la imagen ni en un `--set-env-vars`, sino en Secret Manager.
Cloud Run la monta como variable de entorno al arrancar.

```bash
printf 'sk-or-v1-...' | gcloud secrets create openrouter-key --data-file=-
printf 'su-clave-de-servicio' | gcloud secrets create api-key --data-file=-
```

Y se le da permiso de lectura a la cuenta de servicio con la que corre el
servicio, que por defecto es la de Compute:

```bash
PROY=$(gcloud config get-value project)
NUM=$(gcloud projects describe $PROY --format='value(projectNumber)')
for s in openrouter-key api-key; do
  gcloud secrets add-iam-policy-binding $s \
    --member="serviceAccount:${NUM}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
done
```

## Desplegar

```bash
gcloud run deploy triaje-reclamos \
  --source . \
  --region southamerica-west1 \
  --allow-unauthenticated \
  --set-secrets=OPENROUTER_API_KEY=openrouter-key:latest,API_KEY=api-key:latest \
  --set-env-vars=MODELO=openai/gpt-4o-mini,OTEL_SERVICE_NAME=triaje-reclamos
```

`--source .` compila con el Dockerfile del repositorio, así que no hace falta
construir ni subir la imagen a mano.

`--allow-unauthenticated` deja la dirección abierta a internet, y por eso el
servicio exige su propia `X-API-Key`. Sin esa cabecera devuelve 401, que es
justamente lo que se probó en la sesión 2.

## Las trazas

Para que las trazas lleguen a Langfuse, las dos claves van igual que las
anteriores:

```bash
printf 'pk-lf-...' | gcloud secrets create langfuse-public --data-file=-
printf 'sk-lf-...' | gcloud secrets create langfuse-secret --data-file=-
```

Y se agregan al despliegue:

```
--set-secrets=...,LANGFUSE_PUBLIC_KEY=langfuse-public:latest,LANGFUSE_SECRET_KEY=langfuse-secret:latest
```

Sin ellas el servicio anda igual, solo que no exporta trazas. Para verlas en
el registro de Cloud Run hay que agregar `TRAZAS=consola` a `--set-env-vars` y
leerlo con `gcloud run services logs read triaje-reclamos`.

## La prueba de que está desplegado

```bash
URL=$(gcloud run services describe triaje-reclamos --region southamerica-west1 --format='value(status.url)')
curl -s "$URL/salud"
curl -s -X POST "$URL/reclamos" \
  -H "X-API-Key: su-clave-de-servicio" \
  -H "Content-Type: application/json" \
  -d '{"id":"RCL-999","texto":"Me cobraron dos veces la factura de marzo.","canal":"correo"}'
```

Y la prueba de verdad: mandar esa misma petición desde el celular con datos
móviles. Si responde, está desplegado. Si solo anda en su red, todavía no.

## Apagarlo

```bash
gcloud run services delete triaje-reclamos --region southamerica-west1
```

Conviene probarlo antes de terminar la clase: quien despliega algo tiene que
saber apagarlo.
