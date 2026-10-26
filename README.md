# Nova — Store Operations Agent

> Workflow-first AI agent for a fictional retail operations team. **Educational portfolio project; not production-ready.**

Nova simulates the design, implementation, testing, and evaluation of a special-purpose AI agent for **NovaRetail**, a fictional retailer. All company data, orders, and business metrics are fictitious.

## Business problem and MVP

Store employees need fast, reliable guidance on returns, warranties, and procedures. Hypothetical business objective: reduce supervisor interruptions for routine operational questions by **30%**.

Planned MVP:
1. Answer policy questions using RAG and cite sources.
2. Look up fictional orders and recommend return eligibility using deterministic rules.
3. Clarify ambiguity and escalate unsupported or unauthorized cases.

The Level 1 pilot **does not execute real returns**. Progression: baseline → shadow mode → assisted mode → controlled execution.

## Current implementation

| Milestone | Status | Delivered |
| --- | --- | --- |
| Sprint 0 — Discovery | Complete | Business case, discovery, scope, pilot, architecture |
| Session 1 — Workflow and state | Complete, merged | Deterministic router, conversation state, in-memory store, 7 tests |
| Session 2 — Persistence | Complete, merged | Repository abstraction, SQLite, WorkflowService, restart recovery; 14 total tests |
| Session 3 — LLM intent classification | Complete, merged | Structured classification contract, optional OpenAI adapter, workflow integration; 28 total tests |
| Session 4 — Order verification | Complete, merged | Fictional order lookup, provisional ID, deterministic corroboration, SQLite migration; 43 total tests |
| Session 5 — Product extraction | Complete, merged | Rule-based extraction, regression and uncertainty safeguards, injectable ProductExtractor contract and optional structured OpenAI adapter; 62 tests, 5-case exploratory comparison and 2 successful live end-to-end scenarios |
| Session 6 — Return eligibility | Implemented on feature branch; PR pending | Fictional 30-day window, product condition and category rules; deterministic precedence, explainable results, optional conversational integration; 100 tests and successful user-run end-to-end demo |

**Last user-reported test result:** `100 passed` in GitHub Codespaces on session 6. The user also ran a successful deterministic four-message end-to-end demo yielding `ELIGIBLE` for fictional order 83921 on 2026-10-26. Session 6 is not yet merged. An exploratory comparison of 5 real API examples matched the expected outcomes. Two user-run live end-to-end scenarios also succeeded: direct corroboration and clarification after uncertainty. These are not production reliability benchmarks.

## Architecture (current)

```text
Employee / CLI
      |
WorkflowService  --> StateRepository (in-memory or SQLite)
      |
Deterministic route() --> NovaState

IntentClassifier --> StructuredIntentModel --> optional OpenAIIntentModel
WorkflowService --> optional FakeOrderRepository --> verify_order
WorkflowService --> optional return evaluator --> window + condition + category rules
                                        --> NOT_ELIGIBLE > NEEDS_REVIEW > ELIGIBLE
```

**Design principles:** LLM interprets ambiguous language; Python validates identifiers and business rules; workflow controls transitions; unclear requests ask for clarification instead of guessing. A provisional order ID is corroborated against fictional records before becoming a confirmed reference. Corroboration is not identity verification, authorization or return eligibility. No live order lookup or return execution exists yet.

## Run locally

Requires Python 3.10+.

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m nova
```

The CLI uses SQLite persistence in `nova_state.sqlite3` and demo conversation `demo_001`. The database is ignored by Git. Type `salir` to exit.

Optional real LLM adapter (not required for tests):

```bash
python -m pip install -r requirements-llm.txt
```

Set `OPENAI_API_KEY` in your environment; **never commit API keys**. The optional adapter makes billable API calls when invoked. The CLI currently uses deterministic routing until LLM integration is explicitly enabled.

## Project documentation

- [Business case](docs/01-business-case.md)
- [Discovery](docs/02-discovery.md)
- [MVP scope](docs/03-mvp-scope.md)
- [Pilot design](docs/04-pilot-design.md)
- [Architecture](docs/05-architecture.md)
- [Session 1 — Workflow](docs/06-session-01-workflow.md)
- [Session 2 — Persistence](docs/07-session-02-persistence.md)
- [Session 3 — Intent classification](docs/08-session-03-intent-classification.md)
- [Session 4 — Order verification](docs/09-session-04-order-verification.md)
- [Session 5 — Product extraction](docs/10-session-05-order-details.md)
- [Session 6 — Return eligibility](docs/11-session-06-return-eligibility.md)

## Next steps

- Expand and evaluate structured extraction of order details; improve interruption handling.
- Enable the optional order-verification flow in an interactive demo.
- Improve natural-language understanding of product condition and employee-facing response formatting.
- Enable the opt-in return-evaluation flow in the interactive CLI (currently demonstrated through WorkflowService).
- Add RAG, tool calling, escalation, evaluations, observability, API/UI and deployment.

## Known limitations

No live order system, no policy RAG, no real returns, no production authentication, no concurrency-safe state updates, no formal migration framework beyond the additive SQLite column migration, or retention policy. Model output and external API failures need further hardening before production use.
