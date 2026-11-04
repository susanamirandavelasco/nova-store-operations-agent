"""Conservative evidence-sufficiency prototype for two fictional policy passages.

This is an intentionally narrow, auditable rule baseline, NOT an LLM judge.
Unknown questions abstain. It does not make return eligibility decisions.
"""
from dataclasses import dataclass
import re
import unicodedata

from nova.policy_retrieval import POLICIES, PolicyAnswer, PolicyPassage

ABSTAIN = "No encontré evidencia suficiente en las políticas disponibles para responder esa pregunta."


@dataclass(frozen=True)
class EvidenceDecision:
    supported: bool
    reason: str


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", value).strip()


def assess_evidence(question: str, passage: PolicyPassage) -> EvidenceDecision:
    """Explicitly scoped checks; not a general natural-language understanding model."""
    q = normalize(question)
    t = normalize(passage.text)
    if not q:
        return EvidenceDecision(False, "empty_question")

    # A manufacturer warranty is distinct from acceptance of a return.\n    if re.search(r"garantia.{0,35}fabricante|fabricante.{0,35}garantia", q):\n        return EvidenceDecision(False, "manufacturer_warranty_not_covered")\n\n    # Unsupported topics can share words with a relevant policy.
    if re.search(r"reembols|tarjeta|banco|deposit|acredit|envio|paqueter|horario|sucursal|contrasena|pagar|meses sin intereses", q):
        return EvidenceDecision(False, "unsupported_topic")

    if passage.source_id == "POL-RET-001#plazo":
        if "30 dias naturales" not in t:
            return EvidenceDecision(False, "missing_policy_fact")
        has_time = bool(re.search(r"plazo|dias?|semanas?|mes|periodo|tiempo|vence|vencimiento|cuando|hace [0-9]+|despues de [0-9]+|conteo", q))
        has_return = bool(re.search(r"devol|regres|compr|articulo|producto|conteo de dias|periodo para devolver", q))
        return EvidenceDecision(has_time and has_return, "time_and_return" if has_time and has_return else "topic_not_established")

    if passage.source_id == "POL-RET-001#estado":
        if "revision humana" not in t:
            return EvidenceDecision(False, "missing_policy_fact")
        has_condition = bool(re.search(r"abiert|abri|abrir|caja|empaque|sell|destap|usad|estado|revision|verific|acept|garantiz", q))
        return EvidenceDecision(has_condition, "product_condition" if has_condition else "topic_not_established")

    return EvidenceDecision(False, "unknown_policy")


def answer_if_supported(question: str, passage: PolicyPassage) -> PolicyAnswer:
    decision = assess_evidence(question, passage)
    if not decision.supported:
        return PolicyAnswer(ABSTAIN)
    return PolicyAnswer(passage.text, passage.source_id, passage.title)


def passage_by_source(source_id: str) -> PolicyPassage:
    return next(p for p in POLICIES if p.source_id == source_id)
