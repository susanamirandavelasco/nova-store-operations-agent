"""Conservative extraction tests: interpretation must not decide eligibility."""
import pytest

from nova.condition_extraction import RuleBasedConditionExtractor
from nova.product_condition import ProductCondition


@pytest.mark.parametrize(("message", "expected"), [
    ("SEALED", ProductCondition.SEALED),
    ("Está sellado", ProductCondition.SEALED),
    ("Está sin abrir", ProductCondition.SEALED),
    ("OPENED", ProductCondition.OPENED),
    ("Ya lo abrí", ProductCondition.OPENED),
    ("Está abierto", ProductCondition.OPENED),
    ("DAMAGED", ProductCondition.DAMAGED),
    ("Llegó dañado", ProductCondition.DAMAGED),
    ("Está roto", ProductCondition.DAMAGED),
    ("UNKNOWN", ProductCondition.UNKNOWN),
])
def test_recognizes_unambiguous_condition(message, expected):
    result = RuleBasedConditionExtractor().extract(message)
    assert result.condition == expected
    assert not result.needs_clarification


@pytest.mark.parametrize("message", [
    "",
    "No sé",
    "Creo que está sellado",
    "Está sellado y dañado",
    "No está sellado",
    "Nunca lo abrí, pero está roto",
    "Se ve bien",
])
def test_ambiguous_or_unsupported_description_requires_clarification(message):
    result = RuleBasedConditionExtractor().extract(message)
    assert result.condition is None
    assert result.needs_clarification
