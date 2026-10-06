# Discovery Findings

## Stakeholder

Director of Operations, NovaRetail (fictional).

## Primary concern

The stakeholder is interested in operational assistance but is concerned that an AI agent could incorrectly authorize a return.

This concern materially affects the solution design.

## Discovery decisions

### 1. The LLM will not be the sole authority for critical rules

A prompt such as “do not approve returns older than 30 days” is not considered a sufficient business control.

Critical eligibility conditions should be enforced by deterministic application logic where appropriate.

**Design principle:**

> The LLM can interpret and orchestrate; deterministic controls enforce critical business constraints.

### 2. Human-in-the-loop is part of the product design

Ambiguous, unsupported, conflicting, or unauthorized cases should be escalated rather than guessed.

A good enterprise agent must know not only how to act, but when **not** to act.

### 3. Autonomy should increase progressively

Nova will not begin with unrestricted action capabilities.

Proposed autonomy progression:

- **Level 0 — Recommendation only:** answers using available knowledge.
- **Level 1 — Read + recommend:** can retrieve operational data and recommend an outcome; a human decides.
- **Level 2 — Controlled execution:** may execute explicitly authorized low-risk actions after deterministic validation.
- **Level 3 — Expanded autonomy:** outside the initial MVP and dependent on evidence from prior stages.

### 4. Error types have different business costs

Overall accuracy alone is insufficient.

An incorrect approval can have a materially different impact from an unnecessary escalation.

A key safety metric is therefore the **False Approval Rate**:

> Of cases that should not be approved, how many did the agent incorrectly recommend for approval?

The initial evaluation target for the controlled dataset is **zero false approvals**, accepting that this may initially increase human escalations.

### 5. Technical quality is not sufficient evidence of business value

Even a highly accurate agent is not valuable if it does not improve the operation.

The pilot must therefore measure both:

**AI/system quality**
- decision correctness
- false approval rate
- escalation behavior
- groundedness / evidence use

**Business impact**
- resolution time
- supervisor intervention
- procedural errors
- employee self-service

## Core discovery insight

The business problem should define the architecture.

Requirements such as deterministic guardrails, human escalation, decision logging, evaluation, and progressive autonomy emerged from stakeholder risk and operational needs—not from choosing an AI framework first.
