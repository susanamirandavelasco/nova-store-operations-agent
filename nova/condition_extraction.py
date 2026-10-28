"""Conservative interpretation of an employee's description of product condition.

Interpretation is separate from return eligibility. Ambiguous text never
becomes a definitive condition.
"""
from dataclasses import dataclass
import re
import unicodedata
from typing import Protocol

from nova.product_condition import ProductCondition


@dataclass(frozen=True)
class ConditionExtraction:
    condition: ProductCondition | None
    needs_clarification: bool


class ConditionExtractor(Protocol):
    def extract(self, message: str) -> ConditionExtraction: ...


def _normalize(message: str) -> str:
    decomposed = unicodedata.normalize("NFKD", message.casefold())
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


class RuleBasedConditionExtractor:
    """Small, intentionally conservative vocabulary for the pilot."""

    def extract(self, message: str) -> ConditionExtraction:
        text = _normalize(message).strip()
        if not text:
            return ConditionExtraction(None, True)

        exact = {
            "sealed": ProductCondition.SEALED,
            "opened": ProductCondition.OPENED,
            "damaged": ProductCondition.DAMAGED,
            "unknown": ProductCondition.UNKNOWN,
        }
        if text in exact:
            return ConditionExtraction(exact[text], False)

        # Do not guess from uncertainty, negation or mixed descriptions.
        if re.search(r"\b(creo|quizas|quiza|tal vez|no se|no estoy seguro|no estoy segura|parece|puede que)\b", text):
            return ConditionExtraction(None, True)

        patterns = {
            ProductCondition.SEALED: (r"\bsellad[oa]s?\b", r"\bsin abrir\b"),
            ProductCondition.OPENED: (r"\babiert[oa]s?\b", r"\b(?:lo|la) abri\b"),
            ProductCondition.DAMAGED: (r"\bdanad[oa]s?\b", r"\brot[oa]s?\b"),
        }
        matches = {
            condition for condition, aliases in patterns.items()
            if any(re.search(alias, text) for alias in aliases)
        }
        if len(matches) != 1:
            return ConditionExtraction(None, True)
        # Explicit "sealed, never opened" reinforces a sealed condition.
        # Other negations continue to require clarification.
        if re.search(r"\b(no|nunca|ni)\b", text) and not re.search(r"\bsin abrir\b", text):
            sealed_and_never_opened = (
                matches == {ProductCondition.SEALED}
                and re.search(r"\bsellad[oa]s?\b", text)
                and re.search(r"\bnunca se abrio\b", text)
                and not re.search(r"\bno (?:esta|estaba|venia) sellad[oa]s?\b", text)
            )
            if not sealed_and_never_opened:
                return ConditionExtraction(None, True)
        return ConditionExtraction(next(iter(matches)), False)
