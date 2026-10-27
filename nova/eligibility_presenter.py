"""Present deterministic policy results in employee-friendly Spanish.

Presentation never changes eligibility or authorizes a return.
"""
from nova.eligibility import EligibilityStatus
from nova.eligibility_engine import CombinedEligibilityResult


_HEADINGS = {
    EligibilityStatus.ELIGIBLE: "Elegible para devolución según las reglas del piloto",
    EligibilityStatus.NEEDS_REVIEW: "Se requiere revisión antes de continuar",
    EligibilityStatus.NOT_ELIGIBLE: "No elegible para devolución según las reglas del piloto",
}

_RULE_LABELS = {
    "plazo": "Plazo",
    "condición": "Condición del producto",
    "categoría": "Categoría del producto",
}


def present_eligibility(result: CombinedEligibilityResult) -> str:
    """Render a recommendation; preserve every rule explanation unchanged."""
    heading = _HEADINGS[result.status]
    details = "\n".join(
        f"- {_RULE_LABELS.get(item.rule_name, item.rule_name)}: {item.result.reason}"
        for item in result.evaluations
    )
    if not details:
        details = "- No hay reglas evaluadas; se requiere revisión."
    return (
        f"Recomendación: {heading}.\n"
        f"Motivos:\n{details}\n"
        "Esta recomendación no autoriza ni ejecuta la devolución."
    )
