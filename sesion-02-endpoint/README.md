# Sesión 02 · El endpoint que clasifica

**Construcción de APIs con Flask y FastAPI** · viernes 4 de septiembre

Un servicio que recibe un reclamo en texto libre, se lo pasa al modelo
y devuelve un JSON validado: área, urgencia, confianza y la frase en la que se
apoya. Con la clave en la cabecera y los errores contemplados.

## Cómo se levanta

```bash
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Abra el `.env` y complete los valores de muestra. La aplicación lo lee sola: no
hace falta exportar nada. Si falta una clave o quedó sin completar, el arranque
dice cuál es y dónde ponerla.

```bash
uvicorn app.main:app --reload    # levanta el servicio en el puerto 8000
open http://localhost:8000/docs    # la documentación sale sola del contrato
pytest tests/ -q    # el contrato, sin clave y sin red: ocho pruebas en un segundo
```

## Qué mirar

- `pytest tests/ -q` comprueba los códigos del contrato sin llamar al modelo. Es la forma barata de saber si el endpoint quedó bien.
- `app/verificar.py` es el contraste con sus sistemas, la casilla 6 de la ficha. Un reclamo que cita una factura que el ERP no tiene devuelve **409** y va a revisión humana, sin gastar un token.
- `app/esquemas.py` es el contrato, y se escribe antes que el código.
- Sin la cabecera `X-API-Key` el servicio responde 401; con el texto vacío, 422.
- Una salida que el modelo devuelve mal se reintenta una vez, y después va a 422.

---

Parte del curso **Construcción de Aplicaciones Impulsadas por IA** · BSG Institute.
El mapa de las seis carpetas está en el [README de la raíz](../README.md).
