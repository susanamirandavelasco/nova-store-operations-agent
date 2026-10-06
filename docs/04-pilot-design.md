# Pilot Design

## Objective

Validate Nova's decision quality and operational value before granting execution authority.

The pilot follows a progressive-autonomy approach.

## Phase 0 — Baseline

Measure the current human process before introducing Nova.

Candidate baseline metrics:

- average return-resolution time
- percentage of cases requiring supervisor intervention
- procedural error rate
- escalation volume

Without a baseline, improvement cannot be demonstrated.

## Phase 1 — Shadow Mode

Nova evaluates the same return cases as employees but does not expose its recommendation to the employee and cannot execute actions.

Flow:

```text
Return case
   ├──> Human decision
   └──> Nova recommendation (hidden)
```

The two decisions are recorded independently.

Keeping Nova's recommendation hidden avoids influencing the human decision and makes the comparison more useful.

### Data captured per case

- case ID
- relevant order attributes
- applicable policy/evidence
- Nova recommendation: approve / reject / escalate
- human decision
- validated expected outcome
- reason for disagreement, when applicable
- latency
- model/tool errors

## Phase 2 — Assisted Mode

After acceptable shadow-mode performance, Nova's recommendation becomes visible to employees.

The human remains responsible for the final decision.

Example:

```text
Nova recommendation: REJECT

Reason:
Purchase is outside the permitted return window.

Evidence:
Return Policy RET-001

Final action requires a human.
```

This phase evaluates whether Nova improves the workflow rather than only whether its recommendations are technically correct.

## Candidate metrics

### Safety and decision quality

- False Approval Rate
- recommendation accuracy
- escalation rate
- human/agent agreement rate
- grounded responses / correct policy evidence

### Business impact

- average resolution time
- supervisor-intervention rate
- procedural-error rate

## Initial safety posture

For the controlled evaluation dataset, the initial target is **0% false approvals**.

This target does not imply that a production system can be assumed risk-free. It is an MVP evaluation criterion intended to prioritize conservative behavior before increasing autonomy.

## Exit decision

Evidence from Shadow and Assisted modes determines whether Nova should remain advisory or advance toward **Level 2 controlled execution**, where explicitly authorized low-risk actions can be performed after deterministic validation.
