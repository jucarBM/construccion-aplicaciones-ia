"""OpenTelemetry, y de ahí a Langfuse.

Esto es lo que produce el dibujo de la traza de la sesión 6: cada petición se
abre como un span padre, y cada tramo de adentro cuelga de él. Sin esto, cuando
alguien dice que el sistema está lento no hay con qué contestarle.

Con las claves de Langfuse puestas, las trazas van ahí. Sin ellas y con
TRAZAS=consola, salen por pantalla, que es lo que se muestra en la sesión 6 y
no obliga a nadie a crearse una cuenta. Sin ninguna de las dos cosas no se
exporta nada: en las sesiones 2 a 5 las trazas no interesan todavía y cien
líneas de JSON por petición solo estorban.

Aviso sobre los nombres de atributo: las convenciones gen_ai de OpenTelemetry
todavía están en Development, no son estables. Lo de chat que se usa acá es
lo bastante firme para producción; lo de agentes todavía se mueve.
"""

import base64
import os
from contextlib import contextmanager

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

SERVICIO = os.getenv("OTEL_SERVICE_NAME", "triaje-reclamos")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

_listo = False


def _exportador():
    pk = os.getenv("LANGFUSE_PUBLIC_KEY")
    sk = os.getenv("LANGFUSE_SECRET_KEY")
    if not (pk and sk):
        # Devolver None significa no instalar ningún exportador: se sigue
        # midiendo, pero nada se imprime ni se manda a ningún lado.
        return ConsoleSpanExporter() if os.getenv("TRAZAS") == "consola" else None
    auth = base64.b64encode(f"{pk}:{sk}".encode()).decode()
    return OTLPSpanExporter(
        endpoint=f"{LANGFUSE_HOST}/api/public/otel/v1/traces",
        headers={
            "Authorization": f"Basic {auth}",
            # sin esta cabecera los datos pueden tardar hasta diez minutos
            "x-langfuse-ingestion-version": "4",
        },
    )


def iniciar() -> None:
    """Se llama una vez, al arrancar el proceso."""
    global _listo
    if _listo:
        return
    proveedor = TracerProvider(resource=Resource.create({"service.name": SERVICIO}))
    exportador = _exportador()
    if exportador is not None:
        proveedor.add_span_processor(BatchSpanProcessor(exportador))
    trace.set_tracer_provider(proveedor)
    _listo = True


def tracer():
    iniciar()
    return trace.get_tracer(SERVICIO)


class _SpanModelo:
    """Envuelve el span para que anotar el uso sea una línea y no cinco."""

    def __init__(self, span):
        self._span = span

    def anotar_uso(self, respuesta) -> None:
        uso = getattr(respuesta, "usage", None)
        if uso is None:
            return
        self._span.set_attribute("gen_ai.usage.input_tokens", uso.prompt_tokens)
        self._span.set_attribute("gen_ai.usage.output_tokens", uso.completion_tokens)
        self._span.set_attribute("gen_ai.response.model", respuesta.model)

    def set_attribute(self, clave, valor):
        self._span.set_attribute(clave, valor)


@contextmanager
def span_modelo(modelo: str):
    """El tramo que en la traza se lleva el 67% del tiempo."""
    with tracer().start_as_current_span("chat") as span:
        span.set_attribute("gen_ai.operation.name", "chat")
        span.set_attribute("gen_ai.provider.name", "openrouter")
        span.set_attribute("gen_ai.request.model", modelo)
        yield _SpanModelo(span)


@contextmanager
def span(nombre: str, **atributos):
    """Para los tramos que no son el modelo: validar, consultar el ERP, registrar."""
    with tracer().start_as_current_span(nombre) as s:
        for k, v in atributos.items():
            s.set_attribute(k, v)
        yield s
