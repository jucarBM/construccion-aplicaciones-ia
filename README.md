# Laboratorio · sesión 2

Hoy se construye el primer servicio del sistema de triaje de reclamos: una API
que recibe un mensaje, llama al modelo y devuelve una salida estructurada.

Este repositorio es un **andamio para escribir en clase**. En `main` solo está
la estructura mínima para comenzar. No incluye todavía el chatbot, el lote, la
evaluación ni el despliegue: esas piezas se agregan en las sesiones siguientes.

## Antes de escribir

Necesita Python 3.11 o posterior y dos valores:

- una clave de OpenRouter para que el servicio pueda llamar al modelo;
- una clave propia para proteger el endpoint.

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
```

Abra `.env`, reemplace los dos valores de muestra y deje el archivo fuera del
repositorio. La clave del proveedor y la clave que protege su API son distintas.

## El recorrido de la clase

1. Levante el esqueleto y compruebe `GET /salud`.
2. Escriba `Entrada` y `Salida` en `app/esquemas.py`.
3. Escriba la llamada al proveedor en `app/modelo.py`.
4. Complete `POST /reclamos` en `app/main.py`.
5. Valide la entrada y la salida, y limite los reintentos.
6. Agregue la clave `X-API-Key` y pruebe los errores.

Arranque el servidor:

```bash
uvicorn app.main:app --reload
```

Abra <http://localhost:8000/docs>. También puede comprobar la salud desde otra
terminal:

```bash
curl -s localhost:8000/salud
```

Al terminar, una petición válida se parece a esta:

```bash
curl -s -X POST localhost:8000/reclamos \\
  -H "X-API-Key: su-clave" \\
  -H "Content-Type: application/json" \\
  -d '{"id":"RCL-001","texto":"Me cobraron dos veces la factura de marzo.","canal":"correo"}'
```

La salida contiene `area`, `urgencia`, `confianza` y `evidencia`. El modelo no
calcula devoluciones, no da de baja el servicio y no promete montos ni plazos.

## Punto de control

El laboratorio está listo cuando se cumplen las cuatro condiciones:

- `/docs` abre y muestra `POST /reclamos`;
- sin `X-API-Key`, el endpoint responde `401`;
- un cuerpo inválido responde `422` sin llamar al modelo;
- una entrada válida devuelve la salida del triaje con el esquema acordado.

## Si se traban

Guarde su trabajo y abra la solución de la sesión 2 en otra carpeta:

```bash
cd ..
git clone --branch rescate/sesion-2 \\
  https://github.com/jucarBM/construccion-aplicaciones-ia.git triaje-reclamos-rescate
cd triaje-reclamos-rescate
```

La rama de rescate contiene únicamente la solución de hoy. No es necesario
copiarla al proyecto original ni usarla si el endpoint ya funciona.

## Encargo

Conserve este proyecto: en la próxima sesión se le agregará la conversación
con historial sobre el mismo servicio.
