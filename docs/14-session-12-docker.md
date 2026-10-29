# Session 12 — Docker packaging and Demo 1

## Goal

Run the same Nova walking skeleton (web chat → FastAPI → workflow → SQLite) in a reproducible, single-container local demo. All orders are fictitious and no returns are executed.

## Prerequisites

Docker Engine/Desktop with Compose v2. The Codespaces environment may not provide a usable Docker daemon; check `docker version` and `docker compose version` first.

## Start

```bash
docker compose up --build -d
docker compose ps
docker compose logs --tail=50 nova
```

Open `http://localhost:8000/` for the chat, `http://localhost:8000/docs` for Swagger, and `http://localhost:8000/health` for the liveness check. If running inside Codespaces, use its port-forwarding interface and **keep port 8000 private**. The Compose host binding is loopback-only.

Try: `Quiero devolver unos audífonos` → `83921` → `audífonos` → `Está sellado`.

## Verify SQLite persistence

The Compose named volume `nova_data` stores `/data/nova_state.sqlite3` independently of the container. The browser starts a new conversation after refresh, so verify persistence with an explicit conversation ID through the API:

```bash
curl -s -X POST http://localhost:8000/chat -H 'Content-Type: application/json' -d '{"conversation_id":"docker_persist_01","message":"Quiero devolver unos audífonos"}'
docker compose down
docker compose up -d
curl -s -X POST http://localhost:8000/chat -H 'Content-Type: application/json' -d '{"conversation_id":"docker_persist_01","message":"83921"}'
```

The second response should request the product name rather than restart the conversation. `docker compose down` preserves named volumes; **`docker compose down -v` deletes the database volume**.

## Stop

```bash
docker compose down
```

## Constraints and security

The container runs as a non-root user and with one Uvicorn worker. SQLite is not designed here for concurrent multi-worker writes. The host port binds to `127.0.0.1` only; no TLS, authentication, authorization, application rate limiting, production database or public deployment controls are provided. Do not expose to the public Internet or send real customer data. No OpenAI key is required.

## Validation

**Confirmed in GitHub Codespaces (2026-10-29):** `158 passed, 1 warning in 1.21s`; Docker Engine 29.8.0 and Compose 5.5.1; Uvicorn startup and HTTP 200 for `/health` and web assets; employee chat completed a fictional return recommendation inside Docker. After `docker compose down` and `docker compose up -d`, posting order `83921` to existing conversation `docker_persist_01` returned `next_step=ASK_FOR_ORDER_DETAILS`, confirming SQLite continuity across container recreation. The remaining test warning is a known Starlette/HTTPX deprecation notice. The health check establishes process liveness, not database readiness.

**Demo 1 technical acceptance criteria: met.**
