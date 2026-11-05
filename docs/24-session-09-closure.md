# Session 9 — Closure and Nova V1 scope decision

Status: **closed as an experiment; V3 is NOT integrated**.

## Evidence
The 12 reused development cases gave V3 10/12 exact verdicts, with TP=6, FP=1, FN=1, TN=4. The eight additional edge cases gave 4/8 exact verdicts, with two false-supported and two missed-supported classifications. Across these two small development sets: 14/20 exact verdicts and three false-supported classifications. This is not an estimate of production accuracy. The edge-case results were provided from a live user-run evaluation.

## Decision
- Do not integrate EvidenceVerifierV3 into the Nova V1 chat workflow, eligibility rules, or order operations.
- Keep the existing conservative lexical policy retrieval behavior; do not describe it as fully validated RAG or as guaranteed evidence sufficiency.
- Keep V3 and the evaluation harnesses as isolated, clearly experimental code.
- No more prompt tuning or API experiments are required for Nova V1.
- Continue V1 closure with end-to-end checks, README/architecture documentation and a portfolio demo.

## Explicitly deferred
Evidence-verifier integration is the **last item of the post-V1 backlog** (see docs/25-nova-v1-backlog.md). Future work would need label review, independently selected evaluation questions, a safe fallback, and acceptance criteria before any integration. No claim that V3 meets these criteria.

No change to runtime behavior is part of this session.
