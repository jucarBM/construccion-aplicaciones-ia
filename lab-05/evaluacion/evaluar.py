"""DeepEval sobre respuestas y herramientas capturadas por la API."""

import argparse
import asyncio
from openai import OpenAI
import json
import os
from pathlib import Path

from deepeval.metrics import GEval, ToolCorrectnessMetric
from deepeval.models import DeepEvalBaseLLM
from deepeval.test_case import LLMTestCase, SingleTurnParams, ToolCall, ToolCallParams
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field

RAIZ = Path(__file__).resolve().parents[1]
load_dotenv(RAIZ / ".env")


class Herramienta(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    input_parameters: dict
    output: dict | None = None


class Captura(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    input: str
    actual_output: str
    expected_output: str
    tools_called: list[Herramienta]
    expected_tools: list[Herramienta]
    context: list[str] = Field(min_length=1)
    latencia_ms: int
    trace_id: str | None = None


class SinLLM(DeepEvalBaseLLM):
    """Garantiza que la comparación de herramientas no consume un modelo."""
    def load_model(self):
        return self

    def generate(self, *args, **kwargs):
        raise RuntimeError("La métrica determinista no debe llamar al modelo.")

    async def a_generate(self, *args, **kwargs):
        return self.generate(*args, **kwargs)

    def get_model_name(self):
        return "sin-llm"


class JuezResponses(DeepEvalBaseLLM):
    """Adaptador pequeño: DeepEval pide texto o un esquema Pydantic."""
    def load_model(self):
        return OpenAI(api_key=os.environ["OPENAI_API_KEY"],
                      base_url=os.getenv("OPENAI_BASE_URL") or None, timeout=45)

    def generate(self, prompt, schema=None):
        with self.load_model() as cliente:
            if schema is not None:
                respuesta = cliente.responses.parse(
                    model=self.name, input=prompt, text_format=schema, store=False,
                )
                if respuesta.output_parsed is None:
                    raise RuntimeError("El juez no devolvió el esquema esperado.")
                return respuesta.output_parsed
            respuesta = cliente.responses.create(model=self.name, input=prompt, store=False)
            if respuesta.status != "completed" or not respuesta.output_text:
                raise RuntimeError("El juez no completó la respuesta.")
            return respuesta.output_text

    async def a_generate(self, prompt, schema=None):
        return await asyncio.to_thread(self.generate, prompt, schema)

    def get_model_name(self):
        return self.name


def metricas(usar_juez: bool):
    herramientas = ToolCorrectnessMetric(
        model=SinLLM(model="sin-llm"),
        evaluation_params=[ToolCallParams.INPUT_PARAMETERS],
        should_exact_match=True, threshold=1.0, async_mode=False,
    )
    resultado = [herramientas]
    if usar_juez:
        juez = JuezResponses(model=os.getenv("EVAL_MODEL", "gpt-4o-mini"))
        resultado.append(GEval(
            name="Respuesta de soporte", model=juez, threshold=0.7, async_mode=False,
            evaluation_steps=[
                "Compara la respuesta con la referencia y los resultados reales de herramientas del contexto.",
                "Exige que estado, pedido y condiciones mencionados tengan respaldo. Acepta redacciones distintas.",
                "Si falta el pedido, debe pedirlo. Un registro no encontrado no permite revelar datos de otra persona.",
                "Penaliza afirmar una devolución aprobada o reembolso ejecutado: el sistema solo registra solicitudes para revisión.",
            ],
            evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT,
                               SingleTurnParams.EXPECTED_OUTPUT, SingleTurnParams.CONTEXT],
        ))
    return resultado


def evaluar(archivo: Path, salida: Path, usar_juez: bool):
    capturas = [Captura.model_validate_json(x) for x in archivo.read_text(encoding="utf-8").splitlines() if x.strip()]
    if not capturas or len({x.id for x in capturas}) != len(capturas):
        raise ValueError("La captura debe tener casos con identificadores únicos.")
    reglas = metricas(usar_juez)
    salida.parent.mkdir(parents=True, exist_ok=True)
    aprobados = True
    with salida.open("x", encoding="utf-8") as informe:
        for captura in capturas:
            caso = LLMTestCase(
                name=captura.id, input=captura.input, actual_output=captura.actual_output,
                expected_output=captura.expected_output, context=captura.context,
                tools_called=[ToolCall(**x.model_dump(exclude_none=True)) for x in captura.tools_called],
                expected_tools=[ToolCall(**x.model_dump(exclude_none=True)) for x in captura.expected_tools],
            )
            for regla in reglas:
                regla.measure(caso, _show_indicator=False)
                aprobado = regla.is_successful()
                aprobados = aprobados and aprobado
                fila = {"caso": captura.id, "metrica": regla.__name__, "score": regla.score,
                        "aprobado": aprobado, "razon": regla.reason, "latencia_ms": captura.latencia_ms}
                informe.write(json.dumps(fila, ensure_ascii=False) + "\n")
                informe.flush()
                print(f"{captura.id}: {regla.__name__} = {regla.score:.2f}; {'APROBÓ' if aprobado else 'REVISAR'}")
    return aprobados


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archivo", type=Path, required=True)
    parser.add_argument("--salida", type=Path, required=True)
    parser.add_argument("--juez", action="store_true", help="Consume llamadas al modelo evaluador.")
    args = parser.parse_args()
    raise SystemExit(0 if evaluar(args.archivo, args.salida, args.juez) else 1)
