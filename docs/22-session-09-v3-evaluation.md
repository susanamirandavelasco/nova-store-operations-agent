# Session 9 — V3 validation (scoped increment)

Goal: measure the **existing** three-way evidence verifier, without modifying the prompt, labels, retrieval, chat, or eligibility workflow.

The evaluator reuses the 12 development questions from Session 8. Expected three-way verdicts are specified before the live run. This is a **regression comparison**, not an independent holdout, because V3 was designed after observing these questions.

Historical results on those 12 cases:
- V1: TP=3 FP=0 FN=4 TN=5; precision=1.0, recall=0.429.
- V2: same aggregate metrics.
- V3: **not yet measured**.

```bash
git fetch origin
git switch feature/session-09-v3-evaluation
git pull origin feature/session-09-v3-evaluation
python -m pytest -q
python -m nova.evaluate_evidence_v3
python -m nova.evaluate_evidence_v3 --live
```

The last command makes 12 paid API calls with the configured OpenAI key. Share the printed verdicts and reasons. Review false positives, confusion of negative evidence with missing information, and exact YES/NO polarity. Do not claim success or integrate V3 based solely on the 12 development cases.

The verifier remains experimental and disconnected from Nova's return workflow.
