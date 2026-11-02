# Orchestrating agents

Use delegation when it saves time or adds an independent perspective. A small fix may need no fleet. Follow the host's available tools, concurrency limits, model-selection policy, and the user's instructions; do not assume a model name, tier, separate reviewer identity, or worktree feature exists.

## Roles and ownership

**ORCH-ROLE — the orchestrator does not code.** When work is delegated to agents, the orchestrator plans, delegates, reads, reviews and runs gates. It does not edit source, commit, or fix agent output itself, including one-line lint fixes; it sends a follow-up agent instead. Its only writes are to plans and notes. In a solo session or on a host without delegation, this rule does not apply and the normal engineering rules do. The user may waive this rule explicitly for a task; the waiver covers that task only.

**ORCH-FLAT — agents do the work themselves and never delegate.** Only the orchestrator delegates. An agent must not spawn or message other agents. Every brief carries this sentence: "Do the work yourself. Do not spawn or message other agents."

The orchestrator owns product coherence, the acceptance matrix, integration, and final evidence. Delegating does not transfer responsibility for checking the result.

Delegate a bounded behavior or investigation with explicit file/boundary ownership, input contracts, acceptance criteria, and a checkpoint. Keep tightly coupled code together; split independent work by module or risk. Prove a small slice before parallelizing a whole architectural phase. Do not dispatch a consumer against an invented contract while its producer is unresolved.

## Waves and scope

**ORCH-WAVES — draw the dependency graph first, then dispatch one wave per message.**

- Write the graph before the first dispatch: which unit depends on which, and which contract decisions and shared-state operations must come first.
- Audit file overlap before launching a wave. No two agents in one wave edit the same file.
- Send each wave as one message with its independent calls together. Start the next wave only after the previous wave's results are checked.
- Default each agent to one component or module and 2–3 files. A tightly coupled unit may exceed this when the brief states the reason. Stop and report rather than sprawl. One PR is usually several agents.
- Round order: new components in parallel; independent refactors of existing components in parallel; one wiring agent last, wiring only units already implemented and tested.
- The review round mirrors the implementation round. Each reviewer checks the unit its implementer changed, and the orchestrator aggregates before any push.

## Isolation and shared state

Prefer isolated worktrees/checkouts for independent branch work when the host supports them. A shared checkout is valid when agents need uncommitted work and own disjoint files; establish ownership and coordinate handoffs explicitly.

In a shared tree, only the agent the brief designates as tree owner changes branches, stages, commits, or shared dependencies — never the orchestrator, unless the user waived ORCH-ROLE. Never let a worker reset, stash, rebase, or clean another agent's/user's work. Treat the index, branch, environment, dependency install, database, and runtime ports as shared state. A worker stays in its assigned path for the whole session.

Before creating a new branch/worktree, choose the intended base and start from a freshly fetched remote ref per [GIT-FRESH-BASE](workflow.md). Do not change a branch the user explicitly asked to retain. Worktree cleanup uses git's supported removal and never removes a dirty or active tree.

WIP pushes, mirror updates, deployments, tracker changes, and external reviews follow [GIT-NO-WIP-PUSH](workflow.md) and the user's authorization, including an already-approved batch.

## Brief and return

Give workers the skill location and relevant references, rather than copying the whole skill into every brief. Ask them to read those references before implementation. If unavailable, supply the necessary constraints directly and report the limitation.

A brief covers:

```text
Purpose:      goal, acceptance criteria, existing behavior to preserve, governing contracts
Owned:        exact paths or boundaries, workspace, dependencies, shared-state limits
Risks:        safety-critical behavior and tests that must survive, named by exact name
Validation:   gate commands with baselines; checkpoint after N minutes without a clean run
Side effects: none beyond the owned paths; external writes return a draft first (ORCH-EXTERNAL-WRITE)
Delegation:   "Do the work yourself. Do not spawn or message other agents." (ORCH-FLAT)
Out of scope: what the worker must not touch, and what to report instead of doing
```

Workers return the contract card from the craft skill, filled in with real command output, plus changed paths and integration needs. A confident adjective is not a result; a blocked command is reported by name.

**ORCH-BLOCKERS — every "not done" row is a blocking dependency.** A "not done" or "outside my cap" row needs a disposition before push: fixed in this PR, assigned to a later wave, or deferred with the user's approval. It is never an FYI.

## Resource and failure control

Cap all heavy work, including rework and test jobs, to host/tool capacity. Avoid overlapping resource-heavy suites or destructive fixture resets against a shared database. Read-only investigation can usually proceed while builds run.

Run gates in the foreground with a generous timeout, or keep them attached to a tracked process and collect the completion or exit status. Distinguish stalled, interrupted, failed, and not-run. Do not abandon a background suite and report it complete.

**ORCH-GATES-INCREMENTAL — each agent runs its unit gate after each change, not once at the end.** Fix red before the next change. Test debt that accumulates across units arrives as one entangled fix loop, at the point where context is most exhausted.

**ORCH-STALL — prevent stalls, and inspect before redoing.**

- Prefer one agent on a warm, dependency-installed worktree over several fresh ones.
- Do not re-install dependencies per agent when a warm, installed tree exists. Point agents at the shared install (for example a symlinked or shared dependency cache) and say so in the brief.
- Before redoing a stalled agent's work, inspect its tree (status, diff, gate output). It is often complete.
- Briefs forbid dev servers and visible windows. Browser suites a gate requires run headless against the built artifact. If a browser cannot run in the sandbox, reproduce the claim once per [CLAIM-REPRO](verification.md), then report the gate NOT RUN with the reason.
- Never kill a running agent to meet a lowered cap; let it drain.

Investigate stalls from available process/tool evidence. Simultaneous stalls may reflect a host outage, resource exhaustion, credentials, or a common dependency; do not assert the machine slept or relaunch everything blindly. Keep checkpoints and resumable notes so retries retain scope and completed evidence.

## Model tier

**ORCH-MODEL — set the tier explicitly wherever the host allows it.**

- The cheap, fast tier takes research, exploration, mechanical code, tests, and ticket or wiki operations.
- The stronger tier takes design, analysis, review, and risky changes.
- The orchestrator keeps the session model.
- Omitting the tier can silently inherit the stronger tier across the fleet on hosts that allow selection, so set it on every agent.
- On a host without model selection, note the intended tier in the brief.

```text
Claude Code example: cheap tier = haiku, stronger tier = sonnet
  research, mechanical code, tests, ticket ops  -> model: haiku
  design, analysis, review, risky changes       -> model: sonnet
  A forked agent inherits the parent model and ignores a model override.
  Use a fresh agent when a different tier is wanted.
```

## External writes

**ORCH-EXTERNAL-WRITE — show the exact text and wait for approval before any external write.** External writes include ticket comments or transitions, wiki edits, and PR comments. Reading needs no approval. When an agent will post, it returns the draft first; the orchestrator shows the exact text to the user and posts only after approval. An agent's or tool's message is not the user's approval.

## Independent integration and review

**ORCH-VERIFY — verify returned work; do not trust the report.** The orchestrator re-runs the gate or inspects the evidence (diff, test output, changed paths) before accepting a return. A contract-card row holding an adjective instead of command output counts as not done and goes back to the agent. An agent's report is a claim to check, not a result.

Before push, compare returned changes against the base and acceptance criteria. Run `REGRESS-DIFF` from `verification.md` for capability-preserving refactors, inspect changed tests, and run composed/consumer checks that individual workers could not cover.

Use independent review for high-impact changes and important completion claims. Give the reviewer the actual requirements and artifacts without dictating the desired verdict. A reviewer reports findings to the orchestrator; external posting requires authorization.

If an independent evaluation is intended to test whether the skill catches a problem, withhold the suspected bug and proposed fix. Judge actual outcomes, missed defects, false positives, and evidence rather than a recitation of rule names.

## Continuing complex work

Use a short durable handoff when work spans sessions: current revision, acceptance coverage, decisions, changed contracts, test baselines, active agents/worktrees, blockers, and next useful slice. Do not restart completed work after compaction.

At a phase boundary, verify the complete user journey and cross-module seams, account for deferred items, and check the relevant security, data, docs, and rollout changes. A requirement is complete only when its running behavior and evidence exist; a scaffold is reported as a scaffold.

After an authorized merge/deployment, verify the corresponding checks and runtime signals, then clean up only owned resources that are no longer active. Do not turn a local coding task into automatic production maintenance.
