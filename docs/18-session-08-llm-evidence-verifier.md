# Session 8 — Isolated LLM evidence verifier

This is an **experiment**, not part of the user-facing chat or the deterministic return workflow.

- `LLMEvidenceVerifier` accepts an injected generator for offline unit tests.
- The generator receives a system instruction, question, and the **single** candidate passage.
- Output must be exactly `{"supported": boolean, "reason": string}`.
- Malformed output, API errors, or missing inputs cause abstention.
- `OpenAIEvidenceGenerator` optionally uses `gpt-4o-mini`, `temperature=0`, and JSON object response format. Live calls incur API cost.
- No LLM-generated final answer, no automatic eligibility decisions, and no policy source attribution is issued by this verifier.

**Limitation:** JSON schema validation only proves that the model returned the required shape. It does **not** prove that a `supported=true` judgment is correct. The model can still hallucinate evidence or obey malicious text inside the passage. An independent labeled evaluation and explicit safety checks are required before integration.

## Offline tests

```bash
python -m pytest -q tests/test_llm_evidence_verifier.py
python -m pytest -q
```

## Optional live experiment

```python
from nova.llm_evidence_verifier import LLMEvidenceVerifier, OpenAIEvidenceGenerator
from nova.policy_evidence import passage_by_source

verifier = LLMEvidenceVerifier(OpenAIEvidenceGenerator())
print(verifier.verify("¿Cuánto tarda un reembolso en llegar a mi tarjeta?", passage_by_source("POL-RET-001#plazo")))
```

Compare against manually labeled **unseen** questions before deciding whether to integrate.
