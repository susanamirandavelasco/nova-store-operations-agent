# Session 11 — Web chat walking skeleton

## Goal and delivered scope

Deliver a usable employee-facing chat that exercises the existing HTTP API and deterministic return workflow end to end, without changing the eligibility rules.

- FastAPI serves the HTML page at `/` and CSS/JavaScript at `/ui/` from the same origin as `POST /chat`.
- The page shows employee and Nova messages, disables duplicate submissions while a request is pending, and provides basic error feedback.
- Nova asks about product condition in natural Spanish, and the interface visually distinguishes eligibility recommendations.
- User and server text are inserted using `textContent` rather than interpreted as HTML.
- A fresh conversation ID is generated on each page load and reused for messages until the page is reloaded.

## Run and demonstrate

```bash
python -m pip install -r requirements-dev.txt -r requirements-api.txt
python -m pytest -q
node --check nova/web/app.js
python -m uvicorn nova.api:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/` (web chat) or `/docs` (Swagger). In Codespaces, run Uvicorn with `--host 0.0.0.0` and keep the forwarded port **private**.

Demo flow: `Quiero devolver unos audífonos` → `83921` → `audífonos` → `Está sellado`. All orders are fictitious. Nova recommends eligibility but **does not authorize or execute returns**.

## Verification

Confirmed in Codespaces: **157 passed, 1 warning in 1.42s**. Browser validation confirmed that the web chat completes the fictional return flow and highlights the recommendation. A JavaScript syntax error initially blocked form submission; fixed by removing literal escaped newlines from `app.js`. A new test invokes `node --check` when Node.js is available, and skips with an explicit reason otherwise. The existing Starlette/HTTPX deprecation warning remains.

## Known limitations and backlog

- Refreshing the page generates a new conversation ID; the backend retains earlier state in SQLite, but the browser does **not** restore the visible history.
- After an uncertain network failure, the original message is preserved for manual retry; the request may already have reached the backend, so retries are not guaranteed idempotent.
- No authentication, production security controls, rate limiting, or multi-worker concurrency safety.
- Future work: browser history recovery, structured result cards, real browser automation tests, operational hardening, and Docker packaging (session 12).

This milestone validates the walking skeleton: **web UI → FastAPI → WorkflowService → SQLite and deterministic rules → user-visible response**.
