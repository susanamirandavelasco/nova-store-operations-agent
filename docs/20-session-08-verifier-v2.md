# Session 8 — Evidence verifier prompt v2

## Baseline preserved
Previous run on 20 development cases:
- Rules: TP=9 FP=5 FN=1 TN=5; precision=.643, recall=.90
- LLM v1: TP=4 FP=1 FN=6 TN=9; precision=.80, recall=.40

These figures are **historical**, not a claim about v2.

## Contract change
Prompt v2 defines support as a factual answer that may be **yes or no**, including direct contradiction of an incorrect premise. It also warns against unsupported details and calendar-month/30-day equivalence. Prompt v1 remains accessible for replay.

The existing 20-case dataset and labels were not changed. Some labels remain semantically debatable; they are not a gold standard. For example, 'puede requerir revisión' does not prove that a particular opened item will or will not be reviewed.

## Additional evaluation
12 new development question/passage pairs: 7 labeled answerable, 5 not. They test support with the **correct passage already supplied**, not retrieval. The 12 examples were designed after inspecting previous failures, so do not call them an independent held-out benchmark.

```bash
git pull origin feature/session-08-semantic-retrieval
python -m pytest -q
python -m nova.evaluate_evidence_v2
python -m nova.evaluate_evidence_v2 --live
```

The live comparison runs both prompt versions on the same 12 examples (24 paid OpenAI calls). Keep both verdicts and reasons for manual review. The verifier is still isolated from Nova's workflow.
