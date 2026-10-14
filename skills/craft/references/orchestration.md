# Coordinating agents

Use delegation when it saves time or adds an independent perspective. A small fix may need no fleet. Follow the host's available tools, concurrency limits, model-selection policy, and the user's instructions; do not assume a model name, tier, separate reviewer identity, or worktree feature exists.

## Ownership and decomposition

The coordinating agent owns product coherence, the acceptance matrix, integration, and final evidence. It may implement work directly. Delegating does not transfer responsibility for checking the result.

Delegate a bounded behavior or investigation with explicit file/boundary ownership, input contracts, acceptance criteria, and a checkpoint. Keep tightly coupled code together; split independent work by module or risk, not arbitrary file counts. Prove a small slice before parallelizing a whole architectural phase.

Parallelize reads and independent edits. Sequence contract decisions, dependent wiring, schema/code cutovers, and operations that affect shared state. Do not dispatch a consumer against an invented contract while its producer is unresolved.

## Isolation and shared state

Prefer isolated worktrees/checkouts for independent branch work when the host supports them. A shared checkout is valid when agents need uncommitted work and own disjoint files; establish ownership and coordinate handoffs explicitly.

In a shared tree, only the coordinator changes branches, stages, commits, or changes shared dependencies unless that ownership is delegated. Never let a worker reset, stash, rebase, or clean another agent's/user's work. Treat the index, branch, environment, dependency install, database, and runtime ports as shared state.

Before creating a new branch/worktree, choose the intended base and refresh it when feasible and appropriate. Do not change a branch the user explicitly asked to retain. Worktree cleanup uses git's supported removal and never removes a dirty or active tree.

No automatic WIP pushes, mirror updates, deployments, tracker changes, or external reviews. The user's authorization determines those actions, including an already-approved batch.

## Brief and return

Give workers the skill location and relevant references, rather than copying the whole skill into every brief. Ask them to read those references before implementation. If unavailable, supply the necessary constraints directly and report the limitation.

A useful brief states:
- Purpose, acceptance criteria, existing behavior to preserve, and governing contracts.
- Exact owned paths/boundaries, workspace, dependencies, and shared-state restrictions.
- Relevant risks and the safety-critical behavior/tests that must survive.
- Applicable validation commands and an early checkpoint for unresolved assumptions.
- Allowed side effects, handoff requirements, and what is outside scope.

Workers return changed behavior, paths/symbols, real command results, limitations, and integration needs. Use the evidence card for substantial handoffs. A confident adjective is not a result; a blocked command is reported by name.

## Resource and failure control

Cap all heavy work, including rework and test jobs, to host/tool capacity. Avoid overlapping resource-heavy suites or destructive fixture resets against a shared database. Read-only investigation can usually proceed while builds run.

Keep long commands attached to a tracked process and collect their completion/exit status. Distinguish stalled, interrupted, failed, and not-run. Do not abandon a background suite and report it complete.

Investigate stalls from available process/tool evidence. Simultaneous stalls may reflect a host outage, resource exhaustion, credentials, or a common dependency; do not assert the machine slept or relaunch everything blindly. Keep checkpoints and resumable notes so retries retain scope and completed evidence.

## Independent integration and review

Verify returned changes against the base and acceptance criteria. Run `REGRESS-DIFF` from `verification.md` for capability-preserving refactors, inspect changed tests, and run composed/consumer checks that individual workers could not cover.

Use independent review for high-impact changes and important completion claims. Give the reviewer the actual requirements and artifacts without dictating the desired verdict. A reviewer reports findings to the coordinator; external posting requires authorization.

If an independent evaluation is intended to test whether the skill catches a problem, withhold the suspected bug and proposed fix. Judge actual outcomes, missed defects, false positives, and evidence rather than a recitation of rule names.

## Continuing complex work

Use a short durable handoff when work spans sessions: current revision, acceptance coverage, decisions, changed contracts, test baselines, active agents/worktrees, blockers, and next useful slice. Do not restart completed work after compaction.

At a phase boundary, verify the complete user journey and cross-module seams, account for deferred items, and check the relevant security, data, docs, and rollout changes. A requirement is complete only when its running behavior and evidence exist; a scaffold is reported as a scaffold.

After an authorized merge/deployment, verify the corresponding checks and runtime signals, then clean up only owned resources that are no longer active. Do not turn a local coding task into automatic production maintenance.
