# Nova V1 — Remaining work and deferred backlog

> Planning status after Session 13 merge. **V1 means a reproducible local portfolio pilot, not a production service.** All orders, policies and operational data in the demo are fictional.

## Completed and in progress

| Milestone | Status | Evidence / deliverable |
| --- | --- | --- |
| Session 13 — E2E regression | **Complete, merged** | Eight scenarios reviewed; reported final `main` run: **242 passed, 1 nonblocking warning** |
| Session 14 — Architecture and documentation | **In progress** | Update `docs/05-architecture.md`, `README.md`, and this backlog; review consistency and merge documentation PR |
| Session 15 — Reproducible local demo | **Pending** | Clear setup, scripted fictional scenarios, final portfolio summary and regression run on final `main` |

## V1 completion — remaining work (in order)

### Session 14: Documentation consolidation

- [x] Inspect the implemented architecture and identify runtime vs. optional vs. experimental components.
- [x] Document workflow-first design, component diagram, deterministic eligibility, persistence, and limitations.
- [x] Align README with Session 13 merged status and architecture boundaries.
- [x] Align this backlog with the remaining local V1 work and later cloud phase.
- [ ] Review the documentation diff for accuracy and broken references.
- [ ] Run regression tests (documentation-only change) and merge the PR into `main`.

### Session 15: Reproducible local portfolio demo

- [ ] Provide a concise prerequisites/setup guide for local Python and/or Docker execution.
- [ ] Document a small set of repeatable **fictional** chat scenarios: order corroboration, eligibility recommendation, clarification, policy citation, suspend/resume, and recovery with the same conversation ID.
- [ ] Distinguish manual demo observations from automated test evidence; do not claim live production integrations.
- [ ] Prepare a short portfolio narrative: business problem, architecture choices, implemented scope, measurable test evidence, and limitations.
- [ ] Verify the demo instructions and rerun the full suite on the final `main` branch; record actual results.

**V1 exit criteria:** a reviewer can follow the README, start the local app, reproduce documented scenarios, and understand which features are implemented, optional or experimental. No cloud hosting or production readiness is implied.

## Separate phase after local V1: Production-like cloud deployment

This phase remains part of the **overall Nova project roadmap**, but is **not required for local V1 closure**. Decisions and deliverables are not yet implemented or committed to a provider.

- [ ] Compare AWS and Azure deployment options against learning value, operational complexity, cost and portfolio goals; choose a target architecture.
- [ ] Design infrastructure, environment configuration and secrets management.
- [ ] Add CI/CD with automated test and deployment gates.
- [ ] Address authentication/authorization, safe network exposure and dependency/API failure behavior.
- [ ] Review state storage for concurrency and multiple workers; define migration and retention strategies.
- [ ] Define logging, metrics, traces, health/readiness checks and operational troubleshooting.
- [ ] Establish cost limits and an explicit teardown strategy for cloud resources.
- [ ] Deploy and validate a controlled, fictional end-to-end environment; document known gaps before calling it production-like.

**Boundary:** “production-like” describes deployment practices and controls for a portfolio environment, **not** approval to process real orders, customer data or refunds.

## Post-V1 backlog — final deferred item

**Evidence verifier (LLM) integration — deferred, not a V1 requirement.**

Rationale: V3 generated **three false-supported classifications across 20 development cases** and has not passed an independent safety evaluation. Semantic policy retrieval and verifier experiments are **not integrated into the default chat**.

Potential future acceptance work:

- Review policy scope and expected labels, especially calendar months, gifts, and open-item review.
- Define measurable safety criteria and a new independent evaluation set.
- Consider deterministic guards plus conservative abstention, with explicit limitations.
- Integrate only behind a disabled-by-default flag after review, with end-to-end tests.
- Never let the verifier decide return eligibility or bypass the deterministic workflow.

This verifier integration remains the **last deferred backlog item**, after the local V1 closure and any separately planned cloud work. It must not delay Nova V1 closure.
