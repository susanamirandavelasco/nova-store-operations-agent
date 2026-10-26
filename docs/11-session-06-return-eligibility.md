# Session 6 — Deterministic return eligibility

## Goal and scope

Recommend return eligibility for fictional NovaRetail orders, **without authorizing or executing a return**. The pilot is educational and uses fictional policies and data.

## Rules

1. **Window:** 30 calendar days inclusive. Beyond 30 days is `NOT_ELIGIBLE`; malformed or future dates require review.
2. **Product condition:** `SEALED` is `ELIGIBLE` under this single rule; `OPENED`, `DAMAGED`, and `UNKNOWN` are `NEEDS_REVIEW`, not automatic denials.
3. **Category:** `ELECTRONICS` is `ELIGIBLE`; `PERSONAL_CARE` is `NOT_ELIGIBLE` by fictional policy; `UNKNOWN` requires review.

The combined decision uses **`NOT_ELIGIBLE > NEEDS_REVIEW > ELIGIBLE`**, not majority voting. Every rule's explanation is preserved. `ELIGIBLE` is a recommendation based on these pilot rules, not authorization.

## Implementation

- `nova/eligibility.py`: date-window rule and status/result contracts.
- `nova/product_condition.py`: structured condition rule.
- `nova/product_category.py`: structured category rule.
- `nova/eligibility_engine.py`: combination with explicit precedence and individual explanations.
- `nova/return_evaluator.py`: orchestration of the three pure rules.
- `nova/orders.py`: trusted fictional order category; existing orders default to `UNKNOWN` if omitted.
- `nova/workflow.py`: `ASK_FOR_PRODUCT_CONDITION` state.
- `nova/service.py`: opt-in evaluation through injected `return_evaluator` and `evaluation_date`, following verified order lookup.

A circular-import issue was caught during testing and resolved using `TYPE_CHECKING` and postponed annotations in `eligibility.py`.

## Conversation flow

1. Employee requests return.
2. Nova requests candidate order ID; it remains provisional.
3. Employee confirms product; Nova corroborates the fictional record.
4. With evaluator enabled, Nova requests explicit condition: `SEALED`, `OPENED`, `DAMAGED`, or `UNKNOWN`.
5. Nova evaluates the verified order's purchase date and category plus the employee-provided condition.
6. Nova returns a status and three explanations; it never executes a return.

Without the injected evaluator, the existing order-verification flow remains unchanged. The interactive CLI has **not yet been wired** to this opt-in flow.

## Verification

User ran `python -m pytest -q` in GitHub Codespaces and reported **100 passed**. A user-run four-message end-to-end demonstration for fictional order `83921` (audífonos, electronics), evaluation date 2026-10-26, condition `SEALED`, returned `ELIGIBLE` with all three rule explanations and state `GET_ORDER`.

This demonstration is not a production reliability assessment.

## Limitations and next iteration

- Condition input currently requires exact structured tokens, not natural phrases such as “Está sellado”.
- The final explanation is functional but should be reformatted for employees.
- No real order integration, identity verification, authorization, return execution, policy RAG, or production-grade controls.
- The state `GET_ORDER` is reused after completing evaluation; a dedicated completed state may be clearer in a future iteration.
- Extend scenarios for cancellation, interruptions, unknown categories and edge cases in the next iteration.
