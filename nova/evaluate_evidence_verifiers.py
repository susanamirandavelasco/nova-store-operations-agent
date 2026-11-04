"""Held-out-style evidence sufficiency evaluation, distinct from retrieval ranking.

Run with --live to call OpenAI once per case; default is free/offline.
Cases are development examples, not a statistically representative benchmark.
"""
import argparse
from dataclasses import dataclass

from nova.llm_evidence_verifier import LLMEvidenceVerifier, OpenAIEvidenceGenerator
from nova.policy_evidence import assess_evidence, passage_by_source


@dataclass(frozen=True)
class EvidenceCase:
    question: str
    source_id: str
    supported: bool


CASES = (
    EvidenceCase("¿Tengo treinta días naturales para solicitar una devolución?", "POL-RET-001#plazo", True),
    EvidenceCase("¿El plazo comienza después de comprar?", "POL-RET-001#plazo", True),
    EvidenceCase("¿Puedo iniciar la solicitud el día 25?", "POL-RET-001#plazo", True),
    EvidenceCase("¿El plazo de devolución es de 60 días?", "POL-RET-001#plazo", True),
    EvidenceCase("¿El plazo de devolución se mide en días naturales?", "POL-RET-001#plazo", True),
    EvidenceCase("¿La devolución debe solicitarse dentro de un mes?", "POL-RET-001#plazo", False),
    EvidenceCase("¿Cuántos días tarda el banco en devolverme el dinero?", "POL-RET-001#plazo", False),
    EvidenceCase("¿Puedo devolver una compra internacional?", "POL-RET-001#plazo", False),
    EvidenceCase("¿Se amplía el plazo durante Navidad?", "POL-RET-001#plazo", False),
    EvidenceCase("¿Hay excepciones al límite de 30 días?", "POL-RET-001#plazo", False),
    EvidenceCase("¿Un producto abierto puede necesitar revisión humana?", "POL-RET-001#estado", True),
    EvidenceCase("¿Se garantiza la aceptación de un artículo abierto?", "POL-RET-001#estado", True),
    EvidenceCase("¿Se verifica el estado del producto?", "POL-RET-001#estado", True),
    EvidenceCase("¿La revisión humana es siempre obligatoria para artículos abiertos?", "POL-RET-001#estado", True),
    EvidenceCase("¿La aceptación de un artículo abierto es automática?", "POL-RET-001#estado", True),
    EvidenceCase("¿Cuántos días tarda la revisión humana?", "POL-RET-001#estado", False),
    EvidenceCase("¿Qué empleado revisa un artículo abierto?", "POL-RET-001#estado", False),
    EvidenceCase("¿Debo conservar el ticket para devolver algo abierto?", "POL-RET-001#estado", False),
    EvidenceCase("¿Qué defectos específicos se consideran en la revisión?", "POL-RET-001#estado", False),
    EvidenceCase("¿La garantía del fabricante cubre artículos abiertos?", "POL-RET-001#estado", False),
)


def score(predictions: list[bool]) -> dict[str, float | int]:
    if len(predictions) != len(CASES):
        raise ValueError("Predictions must match case count")
    tp = sum(pred and case.supported for pred, case in zip(predictions, CASES))
    fp = sum(pred and not case.supported for pred, case in zip(predictions, CASES))
    fn = sum(not pred and case.supported for pred, case in zip(predictions, CASES))
    tn = sum(not pred and not case.supported for pred, case in zip(predictions, CASES))
    return {
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "precision": round(tp / (tp + fp), 3) if tp + fp else 0.0,
        "coverage": round(tp / (tp + fn), 3) if tp + fn else 0.0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Use OpenAI API (20 calls; costs money)")
    args = parser.parse_args()
    rules = [
        assess_evidence(case.question, passage_by_source(case.source_id)).supported
        for case in CASES
    ]
    print("Cases:", len(CASES), "supported:", sum(c.supported for c in CASES))
    print("Rules:", score(rules))
    if not args.live:
        print("LLM not run. Pass --live to enable paid API calls.")
        return
    verifier = LLMEvidenceVerifier(OpenAIEvidenceGenerator())
    llm = []
    for i, case in enumerate(CASES, 1):
        result = verifier.verify(case.question, passage_by_source(case.source_id))
        llm.append(result.supported)
        print(f"{i:02d} expected={case.supported} rules={rules[i-1]} "
              f"llm={result.supported} reason={result.reason} | {case.question}")
    print("LLM:", score(llm))
    print("Review disagreements and false positives before integration.")


if __name__ == "__main__":
    main()
