> **Experimental — untested on this platform.** Condensed from the craft skill (skills/craft/). Not extensively tested on GitHub Copilot. Do not rely on it as a compatibility claim.

# Craft rules (condensed)

Copy this file to `.github/copilot-instructions.md`. It summarises the craft skill, which is the source of truth.

## Principles

- Preserve intent: name the requested outcome and the existing behavior that must survive.
- Protect boundaries: derive customer scope from trusted authentication and enforce it at the data or action boundary, including jobs, exports, caches and storage.
- Ground decisions: read the repository's instructions, callers, tests and schema before choosing a pattern. Search for reuse first.
- Keep changes coherent: one useful slice at a time. Flag adjacent cleanup rather than expanding scope.
- Make invariants explicit: use native types, schemas and database constraints.
- Design failure paths: bound external work and retries before adding side effects.
- Prove behavior: run the repository's gates and report actual output. An unrun check is never a pass.
- Keep sensitive content out of telemetry; validate external input and model output.
- Deliver within authorization: keep docs current and write truthful commits.

Severity: `blocker` must not merge; `should-fix` belongs in this change; `nit` is advisory.

## Agents and delegation

If the host delegates work to agents: the orchestrator plans, reviews and runs gates and does not edit source itself (ORCH-ROLE). Agents do the work themselves and never delegate further (ORCH-FLAT). Set the model tier explicitly on each agent (ORCH-MODEL).

## Git and PRs

- Update a feature branch by local rebase, unless repository policy says otherwise, and push with `--force-with-lease` only when pushing is authorized (GIT-REBASE-LOCAL). Do not use the host's update-branch button.
- Push only finished, linter-clean commits (GIT-NO-WIP-PUSH).
- Follow the repository's branch and subject format. The subject describes this commit's diff (GIT-BRANCH-FORM, COMMIT-TRUTH).
- Run the format check, linter and commit-linter as separate gate rows before any push (GATE-FORMAT-LINT).
- A PR adds no new static-analysis vulnerabilities. A suppression needs an owner and an expiry (GATE-VULN-ZERO).
- No assistant attribution, generated-by footer or co-author trailer in commits or PR bodies, unless the project or user asks (COMMIT-NO-ATTRIB).
- Never bypass hooks or branch protection, and never force-push a protected branch.

## Verification

- A gate is proven by its command and actual output. A gate that could not run is reported as `NOT RUN: <reason>` (CLAIM-EVIDENCE).
- Reproduce an agent's "cannot run" claim once before accepting it (CLAIM-REPRO).
- On a refactor, diff against the base for what was lost, not only what was added (REGRESS-DIFF).
- Deleting, skipping or weakening a test to reach green is a blocker. Fix the product, fixture or demonstrably wrong test instead (TEST-NODELETE).
- After a rebase or conflict resolution, compare test counts and test-file line counts with the base (TEST-REBASE-LOSS).

## Stack notes

The repository's own instruction file overrides these notes.

- JVM Maven service: format check first, then compile, unit and integration phases unfiltered. A zero-test run is a failure.
- React TypeScript UI: typecheck, lint, unit tests and production build as separate gates. Follow the repository's styling convention; where it bans inline styles, only assign runtime CSS variables. Never delete an assertion to get green.
- Salesforce Apex and LWC: no SOQL, DML or callouts inside loops. Test at least 200 records.
- Config and deploy repos: name the target environment, paste the rendered diff, keep plaintext secrets out, and state the revert path.
- SQL migrations: never edit an applied versioned migration. Test against a disposable database built from the prior schema.
- LLM-backed features: enforce invariants in code, not only in the prompt. Log no personal or sensitive text.

## Full skill

The complete rules are in the craft skill (`skills/craft/SKILL.md`). This file does not replace it.
