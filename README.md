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
| Session 6 — Return eligibility | Complete, merged | Fictional 30-day window, product condition and category rules; deterministic precedence, explainable results, optional conversational integration; 100 tests and successful user-run end-to-end demo |
| Session 7 — Natural condition + CLI | Complete, merged | Conservative condition extraction, opt-in structured OpenAI condition adapter, Spanish eligibility presenter, fictional CLI demo, SQLite continuity; 141 tests passed in Codespaces and live LLM scenario validated |
| Session 10 — FastAPI API | Complete, merged | `GET /health`, `POST /chat`, HTTP validation, SQLite conversation continuity, regression hardening; 153 tests passed in Codespaces |
| Session 11 — Web chat walking skeleton | Complete, merged | Employee-facing HTML/CSS/JavaScript chat served by FastAPI; natural condition prompt, highlighted recommendations, error handling, JavaScript syntax check; 157 tests passed in Codespaces |
| Session 12 — Docker packaging | Complete | Dockerfile, Compose, persistent SQLite volume, non-root single-worker runtime, healthcheck; Docker chat/persistence validated in Codespaces |
| Session 8 — Policy retrieval and experiments | Complete, merged | Lexical policy retrieval integrated into chat; semantic retrieval, evidence evaluation and V1–V3 verifiers implemented as **isolated experiments**, not wired into chat. 231 tests passed in Codespaces after Session 8. |
| Session 9 — Evidence verifier evaluation | Complete, merged; integration deferred | V3 evaluated on 20 development cases: 14 exact classifications and 3 false-supported verdicts. V3 **not approved for integration**; deferred to the end of the post-V1 backlog. |
| Session 13 — E2E and regression validation | Validated on feature branch; merge pending | Eight scenarios reviewed with explicit evidence scope; SQLite/API continuity regression added; 242 tests passed in Codespaces. |

**Latest confirmed full test run reported:** `242 passed, 1 warning in 1.29s` in GitHub Codespaces on `feature/session-13-e2e-tests` (Session 13; merge pending). This is a feature-branch result, not yet a final run on `main`. Docker chat, health endpoint and SQLite state continuity across container recreation were also validated. The remaining warning is a Starlette/HTTPX deprecation notice; it is not a failing test. Live OpenAI CLI checks confirmed clarification for ambiguous original packaging, `NEEDS_REVIEW` for an opened box, and `ELIGIBLE` for an explicitly sealed product. These exploratory checks are not production reliability benchmarks.

## Architecture (current)

```text
Employee / CLI or web chat (HTML/CSS/JavaScript)
      |
FastAPI HTTP (`/`, `/ui/*`, `POST /chat`)
      |
WorkflowService  --> StateRepository (in-memory or SQLite)
      |
Deterministic route() --> NovaState

IntentClassifier --> StructuredIntentModel --> optional OpenAIIntentModel
WorkflowService --> optional FakeOrderRepository --> verify_order
WorkflowService --> ConditionExtractor (rules or opt-in OpenAI)
WorkflowService --> optional return evaluator --> window + condition + category rules
WorkflowService --> EligibilityPresenter (Spanish, deterministic)
                                        --> NOT_ELIGIBLE > NEEDS_REVIEW > ELIGIBLE
```

**Design principles:** LLM interprets ambiguous language; Python validates identifiers and business rules; workflow controls transitions; unclear requests ask for clarification instead of guessing. A provisional order ID is corroborated against fictional records before becoming a confirmed reference. Corroboration is not identity verification, authorization or return eligibility. No live order lookup or return execution exists yet.

## Run locally

Requires Python 3.10+.

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m nova
python -m nova --demo --conversation prueba_sesion_7
```

The CLI uses SQLite persistence in `nova_state.sqlite3` and default conversation `demo_001`. `--demo` enables fictional order verification and return recommendations, with a separate default conversation ID. Use `--conversation ID` to isolate or resume a session. Fictional orders: `83921` (audífonos, purchased 2026-10-18) and `65042` (televisor, purchased 2026-10-10). The database is ignored by Git. Type `salir` to exit.

Optional real LLM adapter (not required for tests):

```bash
python -m pip install -r requirements-llm.txt
```

Set `OPENAI_API_KEY` in your environment; **never commit API keys**. The optional adapter makes billable API calls when invoked. To use real OpenAI interpretation of the **product condition only**:

```bash
python -m nova --demo --llm-condition --conversation prueba_llm_7
```

Intent classification and product extraction in this CLI mode still use local rules. LLM responses are schema-validated; uncertain descriptions request clarification. API usage may incur charges.

## Run the HTTP API (session 10)

The API reuses the existing `WorkflowService` and SQLite persistence. It uses fictional orders and rule-based condition extraction by default; **no OpenAI API key is required**.

```bash
python -m pip install -r requirements-dev.txt -r requirements-api.txt
python -m pytest -q
python -m uvicorn nova.api:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs` for Swagger UI. In GitHub Codespaces, start Uvicorn with `--host 0.0.0.0` and open the forwarded port's `/docs` page. **Keep the port private.**

- `GET /health` returns `{"status":"ok"}` (process liveness, not database readiness).
- `POST /chat` accepts `{"conversation_id":"demo_api_001","message":"Quiero devolver unos audífonos"}` and returns `conversation_id`, `reply`, `next_step` and `status`.
- Reuse `conversation_id` across messages to resume a conversation. Example continuation: `83921` → `audífonos` → `Está sellado`.
- Invalid, blank, missing or oversized inputs return HTTP 422. `conversation_id` has a 128-character maximum and `message` has a 4,000-character maximum.

This is an **educational local demo**, not a production service: no authentication, production authorization, application rate limiting, concurrency-safe multi-worker state updates or real returns. See [Session 10 — FastAPI HTTP adapter](docs/12-session-10-fastapi.md) for the full contract and limitations.

## Run the web chat (session 11)

Install the API dependencies and run the same FastAPI server shown above. Open `http://127.0.0.1:8000/` (without `/docs`) to use the employee-facing chat. In Codespaces, forward port 8000 privately and open its root URL. The browser sends JSON to `POST /chat` on the same origin; no separate frontend server or OpenAI API key is required.

The chat uses a new conversation ID on each page load and does **not** restore visible history after refresh. A network error preserves the message for manual retry; a previous request might already have reached the backend. The UI is a fictional educational demo and is not suitable for real customer data. See [Session 11 — Web chat walking skeleton](docs/13-session-11-web-chat.md).

## Run Demo 1 with Docker (session 12)

Requires Docker with Compose v2. Run `docker compose up --build -d`, then open `http://localhost:8000/`. The database lives in the named Docker volume `nova_data`, so `docker compose down` preserves it; **`docker compose down -v` deletes it**. The service binds to local loopback only and is **not safe for public exposure**. See [Session 12 — Docker packaging](docs/14-session-12-docker.md) for smoke tests and Codespaces notes. Docker validation completed in Codespaces: the chat returned an eligibility recommendation; after `docker compose down` and `docker compose up -d`, the conversation `docker_persist_01` continued with `next_step=ASK_FOR_ORDER_DETAILS`.

## Policy retrieval and evidence experiments — Sessions 8–9

The fictional demo can now answer explicit policy questions with a source identifier and suspend/resume a return without discarding the pending order. The **runtime uses lexical retrieval**; semantic retrieval and evidence verifiers are implemented only as **isolated experimental modules**, not integrated into the chat or eligibility workflow. V3 was evaluated on 20 development cases (14 exact classifications; 3 false-supported verdicts) and was **not approved for integration**. This is not a validated end-to-end semantic RAG system. See [Session 8 — Policy retrieval](docs/15-session-08-policy-retrieval.md) and [Session 9 — Closure](docs/24-session-09-closure.md).

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
- [Session 10 — FastAPI HTTP adapter](docs/12-session-10-fastapi.md)
- [Session 11 — Web chat walking skeleton](docs/13-session-11-web-chat.md)
- [Session 12 — Docker packaging](docs/14-session-12-docker.md)
- [Session 8 — Policy retrieval (runtime)](docs/15-session-08-policy-retrieval.md)
- [Session 8 — Semantic retrieval experiment](docs/16-session-08-semantic-retrieval.md)
- [Session 8 — Evidence verifier V3 experiment](docs/21-session-08-evidence-verifier-v3.md)
- [Session 9 — Evaluation results](docs/23-session-09-v3-results-and-edge-cases.md)
- [Session 9 — Closure and decision](docs/24-session-09-closure.md)
- [Session 13 — E2E and regression validation](docs/22-session-13-e2e-regression.md)
- [Nova V1 — Remaining work and deferred backlog](docs/25-nova-v1-backlog.md)

## Next steps — Nova V1 closure

1. **Session 13 validated on feature branch:** eight scenarios reviewed, with manual web-chat checks, engine-level boundary verification, and a persisted API-continuity regression; merge and final `main` run pending.
2. **Session 14:** consolidate architecture and final documentation against verified behavior.
3. **Session 15:** prepare the reproducible portfolio demo and confirm the final test run on `main`.

**Post-V1 backlog (last item):** LLM evidence-verifier integration, only after independent evaluation and explicit safety criteria. See [V1 backlog](docs/25-nova-v1-backlog.md). Cloud deployment, production security and observability are not V1 completion requirements.

## Known limitations

Session 13 confirmed that the colloquial phrase “Abrí la caja para revisar el producto” requires condition clarification rather than directly resolving to OPENED. Browser refresh starts a new conversation and does not restore the previous chat history; this does not invalidate SQLite state persistence when the conversation ID is reused. See [Session 13 evidence](docs/22-session-13-e2e-regression.md).

No live order system, no integrated semantic policy RAG (runtime uses lexical retrieval; semantic retrieval is experimental), no real returns, no production authentication, no concurrency-safe state updates, no formal migration framework beyond the additive SQLite column migration, or retention policy. Model output and external API failures need further hardening before production use.
