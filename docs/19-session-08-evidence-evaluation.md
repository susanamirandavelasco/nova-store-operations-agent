# Session 8 — Evidence sufficiency comparison

20 additional manually labeled question/passage pairs (10 answerable, 10 unanswerable).
This tests **evidence sufficiency given a supplied passage**, not retrieval quality.
Labels consider whether the policy provides enough information to answer **yes or no**, including explicitly rejecting an incorrect premise. For example, "¿El plazo es de 60 días?" is answerable using a policy stating 30 days.

**Ambiguity:** "¿La devolución debe solicitarse dentro de un mes?" is labeled unsupported because a calendar month and 30 natural days are not always identical. Review labels before relying on metrics.

Offline:
```bash
python -m pytest -q
python -m nova.evaluate_evidence_verifiers
```

Live experiment (20 OpenAI calls, paid, requires OPENAI_API_KEY):
```bash
python -m nova.evaluate_evidence_verifiers --live
```

Compare TP, FP, FN, TN, precision (TP/(TP+FP)), and coverage/recall (TP/(TP+FN)). Prioritize false positives. This small dataset is for development, not a production safety guarantee. Do not tune on these same cases and call it held-out validation.
