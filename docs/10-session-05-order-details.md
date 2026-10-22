# Session 05 — Product detail extraction (increment 1)

**Goal:** Accept natural-language product descriptions without using the order database to guess what the employee meant.

`extract_product(message) -> ProductExtraction` returns a canonical product name or requests clarification. The initial vocabulary is intentionally limited to **audífonos** and **televisor**; negations, unknown products and multiple products do not produce a guess.

`WorkflowService` now calls the extractor before `verify_order`. Only a single, unambiguous extracted product can be compared with the fictional order. A mismatch or unclear phrase keeps `pending_order_id` and never advances to `GET_ORDER`.

This is a deterministic pilot, not an LLM extraction or a full Spanish language parser. It does not resolve complex negation, synonyms outside the catalog, or multiple products on one order. The existing CLI remains unchanged; use `WorkflowService(..., order_repository=FakeOrderRepository())` for the verified flow.

## Run

```bash
git fetch origin
git switch feature/session-05-order-details-extraction
python -m pytest -q
```

## Next

Replace the deterministic extractor behind the same contract with an optional structured LLM adapter; add evaluation examples and robust interruption handling. Never use an order record to infer a missing user-provided verification detail.

## Increment 2 — Employee uncertainty

A small, explicitly limited set of Spanish uncertainty phrases (for example, `creo que`, `tal vez`, `no estoy seguro`) now blocks order confirmation. The extractor returns `needs_clarification=True` even when a known product appears. The workflow retains the provisional reference until an unambiguous follow-up. This is a deterministic baseline, not a complete uncertainty detector; an LLM adapter must preserve this safety invariant.

## Increment 3 — Dependency inversion

`ProductExtractor` is a `Protocol` exposing `extract(message) -> ProductExtraction`. `RuleBasedProductExtractor` is the default implementation, preserving existing behavior. `WorkflowService` accepts an optional injected extractor, enabling a future LLM adapter or a test stub. Clarification, empty products, and out-of-vocabulary canonical values are rejected before verification. This is an extension point, **not yet a live LLM integration**.
