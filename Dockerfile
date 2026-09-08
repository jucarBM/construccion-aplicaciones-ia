FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8080
WORKDIR /app

COPY requirements.txt requirements-despliegue.txt ./
RUN pip install --no-cache-dir -r requirements-despliegue.txt
COPY servicio ./servicio
COPY crm ./crm
RUN useradd --create-home --uid 10001 appuser && chown -R appuser /app
USER appuser

CMD ["sh", "-c", "uvicorn servicio.main:app --host 0.0.0.0 --port ${PORT}"]
