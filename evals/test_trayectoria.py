"""Cuando el bot usa herramientas, el resultado correcto no alcanza.

Dos agentes pueden llegar a la misma respuesta, uno consultando el ERP una vez
y el otro consultándolo tres. El segundo cuesta el triple y tarda el triple, y
mirando solo la salida los dos aprueban. Por eso se evalúa el camino.

ToolCorrectnessMetric compara las herramientas que se llamaron contra las que
se esperaban. No usa un modelo juez: es comparación directa, así que es barata
y no tiene varianza.

Aviso: las convenciones de evaluación de agentes todavía se están asentando,
tanto en DeepEval como en OpenTelemetry. Esto sirve, aunque conviene revisarlo
cada tanto.
"""

import os

import pytest
from deepeval import assert_test
from deepeval.metrics import ToolCorrectnessMetric
from deepeval.test_case import LLMTestCase, ToolCall

CAMINOS = [
    {
        "id": "consulta-estado",
        "pregunta": "¿En qué quedó mi caso 88-4412?",
        "respuesta": "Su caso está en revisión desde el martes.",
        "usadas": [ToolCall(name="buscar_caso")],
        "esperadas": [ToolCall(name="buscar_caso")],
    },
    {
        "id": "sin-datos",
        "pregunta": "Quiero saber de mi reclamo.",
        "respuesta": "¿Me pasa el número de caso?",
        "usadas": [],
        "esperadas": [],
    },
    {
        "id": "derivar",
        "pregunta": "Quiero que me devuelvan los 5000 soles ya.",
        "respuesta": "Eso lo tiene que ver una persona. Le paso el caso a un asesor.",
        "usadas": [ToolCall(name="derivar_a_humano")],
        "esperadas": [ToolCall(name="derivar_a_humano")],
    },
]


# DeepEval pide la clave del juez incluso para esta métrica, que solo
# compara listas de herramientas y no llama a ningún modelo.
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"),
                    reason="DeepEval exige OPENAI_API_KEY aunque esta métrica no juzgue con modelo")
@pytest.mark.parametrize("caso", CAMINOS, ids=lambda c: c["id"])
def test_camino(caso):
    prueba = LLMTestCase(
        input=caso["pregunta"],
        actual_output=caso["respuesta"],
        tools_called=caso["usadas"],
        expected_tools=caso["esperadas"],
    )
    assert_test(prueba, [ToolCorrectnessMetric()])
