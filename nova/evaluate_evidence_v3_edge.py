"""Eight new, pre-labeled V3 edge cases. Run --live for eight paid calls.

Development validation only; no claim of statistical generalization.
"""
import argparse
from dataclasses import dataclass

from nova.evidence_verifier_v3 import EvidenceVerifierV3, Verdict
from nova.llm_evidence_verifier import OpenAIEvidenceGenerator
from nova.policy_evidence import passage_by_source


@dataclass(frozen=True)
class EdgeCase:
    question: str
    source_id: str
    expected: Verdict


CASES = (
    EdgeCase("¿El conteo de los 30 días empieza con la compra?", "POL-RET-001#plazo", Verdict.SUPPORTED_YES),
    EdgeCase("¿El plazo empieza cuando recibo el paquete?", "POL-RET-001#plazo", Verdict.SUPPORTED_NO),
    EdgeCase("¿Tengo 31 días naturales para solicitar la devolución ordinaria?", "POL-RET-001#plazo", Verdict.SUPPORTED_NO),
    EdgeCase("¿Si compro el 1 de febrero puedo devolver exactamente un mes después?", "POL-RET-001#plazo", Verdict.INSUFFICIENT),
    EdgeCase("¿Las devoluciones de regalos tienen 60 días?", "POL-RET-001#plazo", Verdict.INSUFFICIENT),
    EdgeCase("¿Todos los artículos abiertos requieren obligatoriamente revisión humana?", "POL-RET-001#estado", Verdict.SUPPORTED_NO),
    EdgeCase("¿Un artículo abierto tiene aceptación garantizada?", "POL-RET-001#estado", Verdict.SUPPORTED_NO),
    EdgeCase("¿Los artículos abiertos se rechazan siempre?", "POL-RET-001#estado", Verdict.INSUFFICIENT),
)


def score(verdicts: list[Verdict]) -> dict[str, int]:
    if len(verdicts) != len(CASES):
        raise ValueError("Prediction count mismatch")
    return {
        "exact": sum(v is c.expected for v, c in zip(verdicts, CASES)),
        "false_supported": sum(
            v is not Verdict.INSUFFICIENT and c.expected is Verdict.INSUFFICIENT
            for v, c in zip(verdicts, CASES)
        ),
        "missed_supported": sum(
            v is Verdict.INSUFFICIENT and c.expected is not Verdict.INSUFFICIENT
            for v, c in zip(verdicts, CASES)
        ),
        "wrong_polarity": sum(
            v is not Verdict.INSUFFICIENT
            and c.expected is not Verdict.INSUFFICIENT
            and v is not c.expected
            for v, c in zip(verdicts, CASES)
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Eight paid OpenAI calls")
    args = parser.parse_args()
    print("Eight new labeled edge cases; no workflow integration.")
    print("Expected:", {v.value: sum(c.expected is v for c in CASES) for v in Verdict})
    if not args.live:
        print("No API calls. Pass --live to evaluate V3.")
        return
    verifier = EvidenceVerifierV3(OpenAIEvidenceGenerator())
    verdicts = []
    for i, case in enumerate(CASES, 1):
        result = verifier.verify(case.question, passage_by_source(case.source_id))
        verdicts.append(result.verdict)
        print(f"{i:02d} expected={case.expected.value} got={result.verdict.value} "
              f"reason={result.reason} | {case.question}")
    print("V3 edge cases:", score(verdicts))
    print("Review every error before integration.")


if __name__ == "__main__":
    main()
