"""The presenter preserves policy outcomes and explanations."""
import pytest

from nova.eligibility import EligibilityResult, EligibilityStatus
from nova.eligibility_engine import CombinedEligibilityResult, RuleEvaluation
from nova.eligibility_presenter import present_eligibility


@pytest.mark.parametrize(("status", "heading"), [
    (EligibilityStatus.ELIGIBLE, "Elegible para devolución"),
    (EligibilityStatus.NEEDS_REVIEW, "Se requiere revisión"),
    (EligibilityStatus.NOT_ELIGIBLE, "No elegible para devolución"),
])
def test_statuses_are_presented_in_spanish(status, heading):
    result = CombinedEligibilityResult(
        status,
        (RuleEvaluation("plazo", EligibilityResult(status, "Razón de prueba")),),
    )
    response = present_eligibility(result)
    assert f"Recomendación: {heading}" in response
    assert "Plazo: Razón de prueba" in response
    assert "no autoriza ni ejecuta" in response
    assert result.status == status


def test_all_rule_explanations_are_preserved():
    result = CombinedEligibilityResult(
        EligibilityStatus.NEEDS_REVIEW,
        (
            RuleEvaluation("plazo", EligibilityResult(EligibilityStatus.ELIGIBLE, "Dentro del plazo")),
            RuleEvaluation("condición", EligibilityResult(EligibilityStatus.NEEDS_REVIEW, "Producto abierto")),
            RuleEvaluation("categoría", EligibilityResult(EligibilityStatus.ELIGIBLE, "Electrónica")),
        ),
    )
    response = present_eligibility(result)
    for explanation in ("Dentro del plazo", "Producto abierto", "Electrónica"):
        assert explanation in response


def test_no_evaluations_do_not_claim_eligibility():
    result = CombinedEligibilityResult(EligibilityStatus.NEEDS_REVIEW, ())
    response = present_eligibility(result)
    assert "No hay reglas evaluadas" in response
    assert "Se requiere revisión" in response
