# Triaje de reclamos · laboratorios del curso

Una empresa de servicios recibe **300 reclamos diarios en texto libre**. A lo
largo de seis sesiones se construye el sistema que asiste el triaje: los lee,
dice a qué área van y con qué urgencia, y deja a una persona solo los casos
dudosos.

**Una carpeta por sesión.** Cada una trae el sistema tal como queda al terminar
el laboratorio de ese día, y se levanta sola: su README, su `requirements.txt`
con lo justo y su `.env.example`. Se publican el día de cada clase.

| Sesión | Carpeta | Tema | Fecha |
|---|---|---|---|
| 2 | [`sesion-02-endpoint`](sesion-02-endpoint/) | Construcción de APIs con Flask y FastAPI | viernes 4 de septiembre |
| 3 | _se publica el día de la clase_ | Diseño e implementación de chatbots | viernes 11 de septiembre |
| 4 | _se publica el día de la clase_ | Procesamiento automatizado con IA generativa | viernes 18 de septiembre |
| 5 | _se publica el día de la clase_ | Diseño y validación del proyecto final | viernes 25 de septiembre |
| 6 | _se publica el día de la clase_ | Despliegue y presentación | viernes 2 de octubre |

Como cada carpeta es acumulativa, la de la sesión 5 contiene también lo de la 2,
la 3 y la 4. Comparar una con la anterior muestra exactamente qué se agregó esa
semana.

## Las claves

Ningún archivo de este repositorio tiene una clave. Cada carpeta trae un
`.env.example` con los nombres de las variables; se copia a `.env` y se
completa. El `.env` no se sube: ya está en el `.gitignore`.

Si alguna vez suben una clave por error, no alcanza con borrarla del
repositorio — el historial ya se replicó. Hay que ir al proveedor y revocarla.

## Qué se necesita

Python 3.11 o superior y una cuenta en [OpenRouter](https://openrouter.ai), que
tiene plan gratuito. Las sesiones 5 y 6 agregan DeepEval y OpenTelemetry, ambas
también gratuitas.
