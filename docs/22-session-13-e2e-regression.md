# Session 13 — E2E and regression validation

## Objective

Validate Nova V1's existing return workflow, conservative eligibility recommendations, policy interruption/resumption, and SQLite persistence without expanding production functionality.

## Scenarios and evidence

| ID | Scenario | Outcome | Evidence |
| --- | --- | --- | --- |
| E2E-01 | Verified order 83921, sealed headphones | PASS | Manual web chat; eligible recommendation |
| E2E-02 | Opened product | PASS with clarification | Manual web chat; colloquial description required clarification, explicit "Está abierto" led to review |
| E2E-03 | 31 days after purchase | PASS (engine-level, **not** chat E2E) | Direct `evaluate_return` call; NOT_ELIGIBLE takes precedence |
| E2E-04 | Policy question interrupts a pending return; "Retomar" | PASS | Manual web chat; source `POL-RET-001#plazo`, pending order retained |
| E2E-05 | Nonexistent order 99999 | PASS | Manual web chat; no fabricated order verification |
| E2E-06 | Order 83921 with mismatched product "Televisor" | PASS | Manual web chat; order remains provisional |
| E2E-07 | Unknown condition | PASS | Manual web chat; UNKNOWN produces NEEDS_REVIEW |
| E2E-08 | Persisted pending order and continued workflow | PASS (backend) | Two service instances with shared temporary SQLite; automated HTTP regression test |

E2E-08 was also exercised manually after a browser refresh: the UI did **not** recover the old conversation because it generates a new conversation ID per page load. That behavior is **not** a SQLite persistence failure. A controlled backend check recovered the pending order from SQLite, verified the product, and moved to `ASK_FOR_PRODUCT_CONDITION`. The automated regression `tests/test_session13_persistence.py` recreates the API/service with the same SQLite database, verifies the order and completes an eligible recommendation.

## Automated verification

In GitHub Codespaces on `feature/session-13-e2e-tests`:

```bash
python -m pytest -q tests/test_session13_persistence.py
# 1 passed, 1 warning in 0.52s

python -m pytest -q
# 242 passed, 1 warning in 1.29s
```

The single warning is `StarletteDeprecationWarning` regarding `httpx` and `starlette.testclient`; it did not fail the tests. The reported full-suite result predates the documentation changes; rerun before merging.

## Known V1 limitations

- The phrase "Abrí la caja para revisar el producto" does not directly map to `OPENED`; Nova asks for clarification instead of inferring an unsupported condition.
- The browser chat starts a fresh conversation ID on refresh and does not reload visible history. Backend SQLite persistence works when the same conversation ID is reused.
- The 31-day scenario was tested at the eligibility-engine level, not as a complete web-chat E2E.
- Tests and sample orders are fictional. Nova does not execute returns or provide production-grade identity verification.

## Conclusion

The eight reviewed scenarios showed no critical failures within their stated scope. Session 13 added a focused automated persistence-and-continuity regression without production feature changes. Session 14 will consolidate architecture and documentation; Session 15 will finalize the reproducible portfolio demo.
