# Session 04 — Fictional order verification (first increment)

We distinguish **candidate ID**, **corroborated record**, and **return eligibility**.

- `FakeOrderRepository` is a fake tool with fictional records.
- `verify_order` checks the candidate ID and independently compares employee-supplied details against the record.
- `MATCH` means at least one provided detail matched and none conflicted; it is **not proof of identity, ownership, authorization, or return eligibility**.
- `MISMATCH`, `NOT_FOUND`, and `NEED_MORE_DETAILS` never expose an order record.
- This increment is **not yet connected to WorkflowService, NovaState, SQLite or the CLI**. Provisional IDs and confirmation transitions will follow, with explicit persistence migration.

Run: `python -m pytest -q`.

Next: model `pending_order_id` in persisted state, request corroborating data, and use this tool from the workflow. Before any real data, design authorization, privacy controls, audit logging and a stronger verification policy.

## Increment 2 — Workflow and persistence integration

`WorkflowService(..., order_repository=FakeOrderRepository())` enables the new guarded flow. Without the optional repository, the legacy demo behavior remains unchanged for backward compatibility.

- Exact numeric IDs and the narrowly supported phrase "Creo que era la 83921" become `pending_order_id` and trigger `ASK_FOR_ORDER_DETAILS`.
- Employee-provided product text is compared against the fake record by `verify_order`.
- On `MATCH`, the candidate becomes `order_id` and the workflow reaches `GET_ORDER`; **this is only record corroboration, not identity/ownership verification or return authorization**.
- Mismatch or missing order keeps the candidate provisional; cancellation clears both identifiers.
- SQLite adds `pending_order_id` to existing databases via an additive migration; old records are retained.
- New tests cover matches, mismatches, nonexistent orders, cancellation, restart and legacy database migration.

Try in Codespaces:

```python
from nova.repository import SQLiteStateRepository
from nova.orders import FakeOrderRepository
from nova.service import WorkflowService
service = WorkflowService(SQLiteStateRepository("nova_demo4.sqlite3"), order_repository=FakeOrderRepository())
for message in ("Quiero devolver unos audífonos", "Creo que era la 83921", "audífonos"):
    reply, state = service.handle_message("demo_session4", message)
    print(message, "=>", reply, "|", state)
```

Limitations: not wired into CLI by default; free-form uncertain order expressions are not yet supported; product comparison is exact apart from casing/whitespace; interruption handling is intentionally narrow without a classifier; no real API, customer verification or eligibility rules. The optional classifier needs additional context-aware refinement.
