# Session 8 — Evidence Verifier V3 (experimental)

The previous comparison of 12 question/passage pairs showed **no aggregate improvement** from prompt V1 to V2: each had TP=3, FP=0, FN=4, TN=5. This small development dataset does not establish reliability.

V3 changes the output contract, not just the wording:
- `SUPPORTED_YES`: the supplied passage supports an affirmative answer.
- `SUPPORTED_NO`: it supports a negative answer, including a directly contradicted premise.
- `INSUFFICIENT`: the answer cannot be determined from the supplied passage.

`supported` is derived deterministically from the verdict. Absence of information must not be treated as a negative answer. Malformed outputs, missing input and generator errors fail closed.

The module is **not wired to Nova's workflow or eligibility rules**. Unit tests use fake generators and therefore validate parsing and interface behavior, **not** the actual LLM's accuracy. No paid calls are required for this increment.

Run:
```bash
git pull origin feature/session-08-semantic-retrieval
python -m pytest -q
```

Next session: evaluate V3 with real LLM calls against a manually reviewed dataset, then decide whether to integrate. Do not assume V3 is better before measuring it.
