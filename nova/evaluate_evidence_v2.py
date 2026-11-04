"""Additional, previously untested question/passage pairs for prompt-v2 comparison.

Run offline by default; --live runs both prompt versions on each case (24 paid calls).
These are development cases, not an unbiased production benchmark.
"""
import argparse
from dataclasses import dataclass

from nova.llm_evidence_verifier import (
    LLMEvidenceVerifier, OpenAIEvidenceGenerator, SYSTEM_PROMPT_V1, SYSTEM_PROMPT_V2,
)
from nova.policy_evidence import assess_evidence, passage_by_source


@dataclass(frozen=True)
class Case:
    question: str
    source_id: str
    expected: bool


CASES = (
    Case("¿La solicitud de devolución puede hacerse 10 días después de comprar?", "POL-RET-001#plazo", True),
    Case("¿El límite es de 45 días naturales?", "POL-RET-001#plazo", True),
    Case("¿El plazo se calcula desde la fecha de compra?", "POL-RET-001#plazo", True),
    Case("¿Son 30 días hábiles para devolver?", "POL-RET-001#plazo", True),
    Case("¿Existe una extensión del plazo por enfermedad?", "POL-RET-001#plazo", False),
    Case("¿Puedo cambiar un producto sin recibo?", "POL-RET-001#plazo", False),
    Case("¿Puedo hacer una devolución exactamente un mes calendario después?", "POL-RET-001#plazo", False),
    Case("¿La política asegura que aceptarán un artículo abierto?", "POL-RET-001#estado", True),
    Case("¿Es posible que un producto abierto necesite revisión?", "POL-RET-001#estado", True),
    Case("¿El estado del artículo debe revisarse?", "POL-RET-001#estado", True),
    Case("¿La inspección la hace un gerente?", "POL-RET-001#estado", False),
    Case("¿La revisión tarda menos de 48 horas?", "POL-RET-001#estado", False),
)


def metrics(predictions: list[bool]) -> dict[str, int | float]:
    if len(predictions) != len(CASES):
        raise ValueError("prediction count mismatch")
    tp = sum(p and c.expected for p, c in zip(predictions, CASES))
    fp = sum(p and not c.expected for p, c in zip(predictions, CASES))
    fn = sum(not p and c.expected for p, c in zip(predictions, CASES))
    tn = sum(not p and not c.expected for p, c in zip(predictions, CASES))
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precision": round(tp / (tp + fp), 3) if tp + fp else 0.0,
            "recall": round(tp / (tp + fn), 3) if tp + fn else 0.0}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Compare prompts using 24 paid API calls")
    args = parser.parse_args()
    rules = [assess_evidence(c.question, passage_by_source(c.source_id)).supported for c in CASES]
    print("Additional cases:", len(CASES), "answerable:", sum(c.expected for c in CASES))
    print("Rules:", metrics(rules))
    if not args.live:
        print("No LLM calls. Use --live to compare prompt v1 and v2.")
        return
    generator = OpenAIEvidenceGenerator()
    results = {}
    for name, prompt in (("v1", SYSTEM_PROMPT_V1), ("v2", SYSTEM_PROMPT_V2)):
        verifier = LLMEvidenceVerifier(generator, prompt=prompt)
        predictions = []
        print("\nPrompt", name)
        for i, case in enumerate(CASES, 1):
            decision = verifier.verify(case.question, passage_by_source(case.source_id))
            predictions.append(decision.supported)
            print(f"{i:02d} expected={case.expected} got={decision.supported} "
                  f"reason={decision.reason} | {case.question}")
        results[name] = metrics(predictions)
    print("\nComparison:", results)
    print("Review labels and failures before integration; this is a small development set.")


if __name__ == "__main__":
    main()
