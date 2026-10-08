# Session 02 — State Persistence & Workflow Orchestration

## Decision

A conversation is resumed using the same `conversation_id` even when the CLI process restarts.

## Responsibilities

- `nova.workflow.route()`: deterministic state transitions; does not access storage.
- `nova.service.WorkflowService`: loads state, routes a message, then saves state.
- `nova.repository.StateRepository`: protocol defining `load` and `save`.
- `InMemoryStateRepository`: convenient for tests.
- `SQLiteStateRepository`: durable local SQLite implementation.

## Run

```bash
git switch feature/session-02-state-persistence
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m nova
```

In the CLI, type `Quiero devolver unos audífonos`, then `salir`.
Run `python -m nova` again and enter `83921`. The saved workflow advances to `GET_ORDER`.

The CLI uses a fixed demonstration conversation ID (`demo_001`) and a local file
`nova_state.sqlite3`. Delete that file to reset the demo; do not commit it.

## Constraints and next steps

This is a learning prototype. SQLite is local to one filesystem, and the service's
load-route-save sequence is **not concurrency-safe**: simultaneous requests for the
same conversation can overwrite each other. There is no authorization, encryption,
expiry policy, migrations, or recovery for a corrupt database. Do not store real
employee or customer data. Add versioning / locking and production-grade storage
before multi-user deployment. Keyword intent classification remains a known risk.
