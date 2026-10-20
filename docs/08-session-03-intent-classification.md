# Session 03 — Structured intent classification (part 1)

The LLM interprets employee messages but **does not control workflow transitions**.

## Contract

`IntentResult` contains `intent`, `needs_clarification`, and `clarification_question`. Unknown/invalid output fails closed to a clarification request. The model is instructed not to invent order data or interpret negated cancellations as cancellation commands.

## Design

- `IntentClassifier` validates structured responses and accepts any `StructuredIntentModel`.
- `FakeModel` in tests exercises parsing and safety behavior without API calls.
- `OpenAIIntentModel` is an optional real LLM adapter; install `pip install -r requirements-llm.txt` and configure `OPENAI_API_KEY` in your environment before using it.
- **Not yet wired into `WorkflowService`**. The CLI still uses the deterministic keyword classifier; this is intentional so that integration can be tested as a separate step.
- A real API call costs money; do not commit API keys.
- Later: provisional order identifiers, verification with order lookup, model/network error handling, state-aware classification and explicit safety checks before any side effects.

## Test

```bash
python -m pytest -q
```
