# Session 8 — Evidence sufficiency baseline

## Why
A semantic similarity of 0.4721 connected a bank refund timing question to the 30-day return request policy. Similarity does not establish that the source answers the question.

## This increment
`nova/policy_evidence.py` provides a deliberately narrow, offline evidence gate for the two fictional policies. It checks topic indicators **and the presence of the relevant fact in the passage**, rejects some known unsupported topics, and abstains without a source when uncertain.

It is a rule-based prototype, **not a general verifier, LLM judge, or entailment model**. Keyword heuristics can miss paraphrases and may accept unsupported questions; passing unit tests does not prove safety or reliability.

No workflow integration and no eligibility decision changes. Next: score the gate on unseen labeled questions, inspect false positives/negatives, and consider a grounded LLM verifier with explicit support/insufficient-evidence output.

## Run
```bash
python -m pytest -q tests/test_policy_evidence.py
python -m pytest -q
```
