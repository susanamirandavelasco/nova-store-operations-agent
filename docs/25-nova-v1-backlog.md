# Nova V1 — Remaining work and deferred backlog

## V1 completion (in order)
1. Run end-to-end regression scenarios for the existing return workflow, including ambiguous order/product, suspend/resume, eligibility outcomes, policy abstention and unavailable dependencies.
2. Consolidate README and architecture description with accurate implemented-versus-experimental boundaries.
3. Prepare a reproducible demo and final portfolio summary; confirm test results on the final main branch.

## Post-V1 backlog — final item
**Evidence verifier (LLM) integration — deferred, not a V1 requirement.**

Rationale: V3 generated three false-supported classifications across 20 development cases and has not passed an independent safety evaluation.

Potential future acceptance work:
- Review policy scope and expected labels, especially calendar months, gifts, and open-item review.
- Define measurable safety criteria and a new independent evaluation set.
- Consider deterministic guards plus conservative abstention, with explicit limitations.
- Integrate only behind a disabled-by-default flag after review, with end-to-end tests.
- Never let the verifier decide return eligibility or bypass the deterministic workflow.

This item is intentionally **last** and must not delay Nova V1 closure.
