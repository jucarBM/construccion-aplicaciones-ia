"""El evaluador de la sesión 5, corriendo bajo pytest.

Dos clases de medición, y conviene no confundirlas:

  1. Lo que se puede comparar con ==. El área y la urgencia salen de una lista
     cerrada, así que ahí no hace falta ningún juez: se cuenta y listo. Es más
     barato, más rápido y no tiene varianza.

  2. Lo que no. Si la evidencia citada sostiene la decisión es un juicio, y para
     eso está GEval: un modelo evaluando con criterios escritos en castellano.
     Eso es agent-as-a-judge, y hay que validarlo contra personas antes de
     confiar en él.

    pytest evals/                 # local
    deepeval test run evals/      # con el informe de DeepEval

Necesita una clave para el modelo juez, aparte de la del servicio.
"""

import json
import os
import pathlib

import pytest
from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams

from app.esquemas import Salida
from app.modelo import triar

CONJUNTO = pathlib.Path(__file__).parent / "conjunto.jsonl"


def casos():
    """Los cincuenta que etiquetaron a mano. Congelados: si se agregan casos
    cada vez que algo falla, los números dejan de ser comparables."""
    return [json.loads(l) for l in CONJUNTO.read_text(encoding="utf8").splitlines() if l.strip()]


# Cada caso se manda al modelo una sola vez por corrida. Antes `test_area` y
# `test_acierto_global` lo pedían cada uno por su lado: cien llamadas para medir
# cincuenta casos, el doble de plata y el doble de espera dentro del punto de
# control. El resultado se guarda acá y las dos pruebas leen lo mismo.
_salidas: dict[str, Salida] = {}


def salida(caso) -> Salida:
    if caso["id"] not in _salidas:
        _salidas[caso["id"]] = Salida.model_validate(triar(caso["texto"]))
    return _salidas[caso["id"]]


# --- 1. lo que se compara con == -------------------------------------------

@pytest.mark.parametrize("caso", casos(), ids=lambda c: c["id"])
def test_area(caso):
    """Ojo: se espera que algunos fallen.

    La línea de base es 76% de acierto, así que sobre cincuenta casos hay una
    docena en rojo y eso NO significa que el laboratorio esté roto: son los
    casos que el modelo no clasifica como la persona que los etiquetó. El
    número que dice si el sistema está bien es `test_acierto_global`. Estos
    cincuenta sirven para mirar cuáles falla, que es distinto.
    """
    s = salida(caso)
    assert s.area == caso["area"], f"esperaba {caso['area']}, devolvió {s.area}"


def test_acierto_global():
    """El número que va al informe. Falla si cae por debajo de la línea de base.

    76% sale de 38 sobre 50, y el techo es el acuerdo entre dos personas, que
    en este conjunto dio 78%. Pedirle más al modelo que a las personas no
    tiene sentido."""
    todos = casos()
    aciertos = sum(salida(c).area == c["area"] for c in todos)
    total = len(todos)
    acierto = aciertos / total
    print(f"\nacierto {aciertos}/{total} = {acierto:.0%}")
    assert acierto >= 0.70, f"el acierto cayó a {acierto:.0%}"


# --- 2. lo que necesita un juez --------------------------------------------

def evidencia_sostiene():
    """El juez se arma dentro de la prueba, no al importar el archivo.

    Construirlo arriba obligaba a tener la clave del juez para que pytest
    pudiera siquiera recolectar, y entonces las dos pruebas de == tampoco
    corrían. Así, quien no tenga esa clave sigue pudiendo medir el acierto.
    """
    return GEval(
        name="La evidencia sostiene la decisión",
        evaluation_steps=[
            "Verifica que la evidencia sea una frase textual del mensaje de entrada, no un resumen.",
            "Verifica que esa frase justifique el área asignada.",
            "Penaliza que la evidencia esté vacía o sea genérica.",
            "No penalices diferencias de redacción ni de mayúsculas.",
        ],
        evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
        threshold=0.7,
    )


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"),
                    reason="hace falta la clave del modelo juez (OPENAI_API_KEY)")
@pytest.mark.parametrize("caso", casos()[:10], ids=lambda c: c["id"])
def test_evidencia(caso):
    s = salida(caso)
    prueba = LLMTestCase(
        input=caso["texto"],
        actual_output=f"área: {s.area} · evidencia: {s.evidencia}",
        expected_output=caso["area"],
    )
    assert_test(prueba, [evidencia_sostiene()])
