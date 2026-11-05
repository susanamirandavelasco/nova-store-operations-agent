"""Evaluate experimental V3 against the SAME 12 development cases used for V1/V2.

This is a regression comparison, NOT an independent holdout. Live mode makes
12 paid API calls. No workflow integration or eligibility decisions.
"""
import argparse

from nova.evidence_verifier_v3 import EvidenceVerifierV3, Verdict
from nova.evaluate_evidence_v2 import CASES, metrics
from nova.llm_evidence_verifier import OpenAIEvidenceGenerator
from nova.policy_evidence import passage_by_source

# Labels fixed before the V3 live run; ambiguous cases require manual review.
# A false premise directly contradicted by the policy is SUPPORTED_NO.
EXPECTED_VERDICTS = (
    Verdict.SUPPORTED_YES,  # 01: day 10 within 30
    Verdict.SUPPORTED_NO,   # 02: 45 vs 30
    Verdict.SUPPORTED_YES,  # 03: from purchase
    Verdict.SUPPORTED_NO,   # 04: business vs natural days
    Verdict.INSUFFICIENT,   # 05: illness extension not specified
    Verdict.INSUFFICIENT,   # 06: receipt requirement not specified
    Verdict.INSUFFICIENT,   # 07: calendar month is not 30 natural days
    Verdict.SUPPORTED_NO,   # 08: acceptance not guaranteed
    Verdict.SUPPORTED_YES,  # 09: review may be required
    Verdict.SUPPORTED_YES,  # 10: condition must be checked
    Verdict.INSUFFICIENT,   # 11: manager not specified
    Verdict.INSUFFICIENT,   # 12: inspection duration not specified
)


def evaluate(verdicts: list[Verdict]) -> dict:
    if len(verdicts) != len(CASES):
        raise ValueError("Expected exactly 12 verdicts")
    support_metrics = metrics([v is not Verdict.INSUFFICIENT for v in verdicts])
    exact = sum(got is expected for got, expected in zip(verdicts, EXPECTED_VERDICTS))
    return {"exact_verdicts": exact, "total": len(CASES), **support_metrics}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Run 12 paid OpenAI calls")
    args = parser.parse_args()
    assert len(CASES) == len(EXPECTED_VERDICTS)
    assert all(c.expected == (v is not Verdict.INSUFFICIENT)
               for c, v in zip(CASES, EXPECTED_VERDICTS))
    print("Dataset: 12 previously used development cases (not held-out)")
    print("Historical V1 and V2: TP=3 FP=0 FN=4 TN=5, precision=1.0, recall=0.429")
    print("Gold-label breakdown:", {v.value: EXPECTED_VERDICTS.count(v) for v in Verdict})
    if not args.live:
        print("Offline: no model calls. Pass --live for V3 (12 paid calls).")
        return
    verifier = EvidenceVerifierV3(OpenAIEvidenceGenerator())
    verdicts = []
    for i, (case, expected) in enumerate(zip(CASES, EXPECTED_VERDICTS), 1):
        result = verifier.verify(case.question, passage_by_source(case.source_id))
        verdicts.append(result.verdict)
        print(f"{i:02d} expected={expected.value} got={result.verdict.value} "
              f"reason={result.reason} | {case.question}")
    print("V3:", evaluate(verdicts))
    print("Manually review false positives and verdict disagreements before integration.")


if __name__ == "__main__":
    main()
