# Session 04 — Fictional order verification (first increment)

We distinguish **candidate ID**, **corroborated record**, and **return eligibility**.

- `FakeOrderRepository` is a fake tool with fictional records.
- `verify_order` checks the candidate ID and independently compares employee-supplied details against the record.
- `MATCH` means at least one provided detail matched and none conflicted; it is **not proof of identity, ownership, authorization, or return eligibility**.
- `MISMATCH`, `NOT_FOUND`, and `NEED_MORE_DETAILS` never expose an order record.
- This increment is **not yet connected to WorkflowService, NovaState, SQLite or the CLI**. Provisional IDs and confirmation transitions will follow, with explicit persistence migration.

Run: `python -m pytest -q`.

Next: model `pending_order_id` in persisted state, request corroborating data, and use this tool from the workflow. Before any real data, design authorization, privacy controls, audit logging and a stronger verification policy.
