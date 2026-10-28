# Session 10 — FastAPI HTTP adapter

## Goal

Expose Nova's existing deterministic workflow through HTTP without duplicating business rules. This is a fictional, local educational demo, **not production-ready**.

## Install and run

```bash
python -m pip install -r requirements-dev.txt -r requirements-api.txt
python -m pytest -q
python -m uvicorn nova.api:app --reload --host 127.0.0.1 --port 8000
```

Visit `http://127.0.0.1:8000/docs`. In GitHub Codespaces, open the forwarded port and append `/docs`. Keep forwarded port visibility **private**.

## HTTP contract

- `GET /health`: returns HTTP 200 and `{"status":"ok"}`. Liveness only, not database readiness.
- `POST /chat`: accepts a JSON object with `conversation_id` (nonblank, at most 128 characters) and `message` (nonblank, at most 4000 characters).
- Success returns HTTP 200 with `conversation_id`, `reply`, `next_step` and `status`.
- Invalid, missing, blank or oversized fields return HTTP 422; `GET /chat` returns 405.
- Use the same conversation ID across requests to resume state from SQLite (`nova_state.sqlite3`); different IDs have separate states.

Example request:

```json
{"conversation_id":"demo_api_001","message":"Quiero devolver unos audífonos"}
```

Example continuation: `83921` → `audífonos` → `Está sellado`. These are fictional orders and the result is a recommendation, **never authorization or execution of a return**.

## Architecture and boundaries

FastAPI validates input and serializes output; `WorkflowService` retains conversation orchestration, `SQLiteStateRepository` persists state, and deterministic rules evaluate eligibility. `create_app(service)` supports dependency injection for isolated HTTP tests. The API uses rule-based extraction by default and makes **no OpenAI calls**.

This increment does not include authentication, authorization, production CORS configuration, application rate limiting, concurrency-safe multi-worker state updates, error observability, or a production database. Do not expose publicly or send real customer data.

## Validation and known issue

Session 10 initially passed 146 tests in Codespaces (one Starlette/httpx deprecation warning). Additional negative and contract tests were added afterward; rerun the full suite before merging. The warning should be reviewed with compatible dependencies rather than suppressed. The post-evaluation state `GET_ORDER` does not yet represent an explicit end-of-conversation state.

## Delivery plan

Session 11 adds the web chat UI, session 12 Docker for local Demo 1, sessions 8–9 add RAG/evaluation for Demo 2, and sessions 13–15 cover cloud deployment, operational hardening, and portfolio Demo 3.
