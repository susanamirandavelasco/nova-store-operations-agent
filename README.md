# Nova — Store Operations Agent

> Production-oriented Special Purpose AI Agent (SPA) for retail operations.

Nova is a portfolio project that simulates the design, evaluation, and deployment of an enterprise AI agent for a fictional retail company, **NovaRetail**.

The project intentionally starts with the **business problem and discovery process**, rather than with a framework or model.

## Business problem

Frontline store employees frequently need help with returns, warranties, promotions, and internal procedures. The information exists, but is distributed across operational documentation, so employees often interrupt supervisors for help.

**Hypothetical business objective:** reduce operational questions requiring supervisor intervention by **30%**.

> All company names, operational data, orders, customers, and business metrics in this repository are fictional and created for educational/portfolio purposes.

## MVP

Nova will initially support three capabilities:

1. **Knowledge** — answer questions about returns, warranties, and promotions using internal documentation and cite the relevant source.
2. **Order lookup and return recommendation** — retrieve a fictional order, apply the relevant policy and recommend an outcome.
3. **Escalation** — recognize ambiguous, unsupported, or unauthorized cases and route them to a human.

Critical business rules will not rely solely on probabilistic LLM reasoning. Deterministic controls will be used where incorrect execution creates business risk.

## Pilot strategy

The project models progressive autonomy:

**Baseline → Shadow Mode → Assisted Mode → controlled execution**

The first pilot does not allow the agent to execute real returns. Human and agent decisions are captured independently and evaluated before increasing autonomy.

## Planned technical journey

The implementation will progressively cover:

- LLM orchestration
- Retrieval-Augmented Generation (RAG)
- Tool calling
- Deterministic guardrails
- Human-in-the-loop
- Automated evaluation
- Observability
- API and UI
- Docker
- CI/CD
- Cloud deployment

The architecture and technology choices will be documented as the project evolves.

## Documentation

- [Business case](docs/01-business-case.md)
- [Discovery findings](docs/02-discovery.md)
- [MVP scope](docs/03-mvp-scope.md)
- [Pilot design](docs/04-pilot-design.md)
- [Architecture](docs/05-architecture.md)

## Status

**Sprint 0 — Discovery and solution definition**
