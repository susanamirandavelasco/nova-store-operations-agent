# Session 01 — Workflow state and router

## Purpose

Learn deterministic workflow orchestration before introducing an LLM or agent framework.

## Run in Codespaces

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m nova
```

Suggested dialogue:

1. `Quiero devolver unos audífonos`
2. `Mejor dime la política de garantía`
3. `retomar`
4. `83921`

## Architecture

- `NovaState`: business context plus workflow position and lifecycle.
- `classify_message`: temporary keyword-based intent classifier.
- `route`: deterministic transitions.
- `InMemoryConversationStore`: state scoped to a conversation ID.
- `tests/test_workflow.py`: repeatable state-transition tests.

## Deliberate limitations

- No LLM, RAG, order lookup, or actual return execution.
- The classifier is **not safe for production** (e.g. negation can be misunderstood).
- An order ID is accepted only when the entire message is digits.
- Suspended workflows require explicit resumption.
- Storage is process-local and not persistent.
- Only one pending return workflow per conversation.
- Authorization, audit, expiration, and policy versioning are future work.

## Next design question

Should a suspended workflow resume implicitly when the employee sends an order number, or require an explicit resume instruction?
