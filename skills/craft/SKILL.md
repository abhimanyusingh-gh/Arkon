---
name: craft
description: Build, change, and review production applications with explicit requirements, coherent architecture, safe data boundaries, and demonstrated behavior. Use for application development, complex features, refactors, debugging, and engineering reviews on any stack.
---

# Craft

Use this skill to turn a product request into working, verifiable software. Scale the process to the risk: a local fix needs a short investigation; a complex application needs explicit contracts and an incremental delivery plan. User instructions and repository requirements take precedence over these defaults. This skill grants no permission to publish, deploy, contact people, or mutate external systems.

## Working invariants

1. **Preserve intent.** Name the requested outcome and existing behavior that must survive. Trace requirements to running code and meaningful checks. Never delete a capability or weaken its test just to obtain green gates.
2. **Protect boundaries.** Derive identity and customer scope from trusted authentication. Enforce authorization at the data/action boundary, including jobs, exports, caches, and storage. A cross-customer leak is a blocker.
3. **Ground decisions.** Read the repository's instructions, callers, tests, schema, and CI before choosing patterns. Search for reuse; prefer the existing coherent design over a new parallel framework.
4. **Keep changes coherent.** Implement one useful slice at a time. Preserve unrelated behavior; flag adjacent cleanup rather than expanding scope. Choose the simplest design that satisfies the actual constraints.
5. **Make invariants explicit.** Use the language's native types, schemas, and database constraints. Brand or wrap values where a real mix-up is possible; reuse existing finite-value types. Type assertions do not validate external input.
6. **Design failure paths.** Bound external work and retries; specify partial failure, concurrency, duplicate delivery, and recovery before adding side effects. Do not claim exactly-once behavior from a lease alone.
7. **Prove behavior.** Run the applicable repository gates and report their actual output, skips, and limitations. Verify real composition and lost capabilities as well as individual units. An unrun check is never a pass.
8. **Keep sensitive content out of telemetry.** Validate external input and model output; minimize disclosed data. Security and privacy guarantees require negative tests at the relevant boundary.
9. **Deliver within authorization.** Keep docs current, use truthful commits, and respect existing approval and branch-protection rules. Commit, push, open a PR, merge, and deploy only within the user's authorized scope. Never add assistant attribution or co-author trailers.

Severity: `blocker` means unsafe or broken behavior that must not ship; `should-fix` belongs in this change; `nit` is advisory. Severity follows demonstrated impact, not the number of style violations.

## Application workflow

For a new application or work spanning multiple boundaries, read `references/application-design.md` first.

1. **Discover.** Bind the real stack and environment. Identify acceptance criteria, protected behavior, and unknowns. Ask only about decisions whose answers would materially change the implementation; continue independent work.
2. **Design the risky seams.** State ownership, contracts, data invariants, and failure behavior. Verify an uncertain integration with the smallest useful spike. Use `references/history.md` when deriving standards from commit history; distinguish observed fixes from preferences.
3. **Build a vertical slice.** Connect a real entry point through business logic and persistence to an observable result. Run focused checks while iterating, then add the next slice. Avoid completing every layer before any user journey works.
4. **Verify and deliver.** Compare against acceptance criteria and the base revision, run applicable full gates, and check the production artifact and rollout when relevant. Report omissions and blockers by name; do not present scaffolded or mocked integrations as complete.

## Evidence card

Use this compact return format for substantial work and agent handoffs; a small fix can report the same evidence in prose. Omit irrelevant rows with a reason rather than inventing work.

```text
CRAFT CONTRACT
  References read     craft + [relevant references]
  Acceptance          criterion -> implemented path -> test or observed result
  Scope / reuse       changed boundaries; reused symbols or reason for new code
  Safety              scope/auth invariant; failure/recovery behavior | N/A: reason
  Capability check    base revision; preserved/changed/removed behavior + evidence
  Tests changed       named contract change or replacement coverage | none
  Gates               command -> result/counts/skips; revision tested
  Not run             check -> reason and remaining uncertainty | none
  Delivery            migration/rollout/recovery evidence | N/A: reason
  Not done            explicit omissions and consequences | none
```

A row containing only “done,” “safe,” or “all tests pass” is unfilled. `NOT RUN: <reason>` is valid evidence of a limitation. Re-run checks affected by later changes and identify which revision each result covers. Read `references/verification.md` when assessing an agent's completion claims.

## Project bindings

Derive these from the actual repository; keep them in working notes or an existing project-approved location. Do not create or rewrite instruction files merely to use this skill.

```text
Commands      package/task runner; typecheck; unit/integration; build; e2e; lint/deadcode
Boundaries    deployable units; shared libraries; API/event consumers; external services
Data          datastore/version; migrations; customer scope key; retention; test isolation
Runtime       startup/readiness; config/secrets; background workers; telemetry
Delivery      CI; base revision/remote; deployment topology; rollback mechanism
Product       acceptance criteria; design source; tracker/issue when one exists
```

## References — load when the work reaches that boundary

Read relevant references before designing or changing that boundary. A task may need several, loaded as needed rather than all at once. Examples and historical fixes are not universal stack requirements.

| Trigger | Read |
|---|---|
| New application, complex feature, architecture or domain design | `references/application-design.md` |
| Deriving conventions from commit history or adapting this skill | `references/history.md` |
| Authentication, permissions, public input, uploads, URLs, secrets | `references/security.md` |
| Customer data, queries, storage paths or cache keys | `references/tenancy.md` |
| Production code, types, naming, config, layering or indices | `references/authoring.md` |
| External API, event consumer, transaction spanning a side effect | `references/integrations.md` |
| UI state, visual design or client data flow | `references/frontend.md` |
| Interactive components, forms, dialogs or announcements | `references/accessibility.md` |
| Scheduled job, poller, queue, claim, lease or manual trigger | `references/async-jobs.md` |
| Logs, exception handling, metrics, traces or error bodies | `references/observability.md` |
| External model call, prompt, output validation or AI-assisted action | `references/llm-calls.md` |
| Dependencies, platform upgrades, advisories or suppressions | `references/dependencies.md` |
| Writing or changing tests | `references/testing.md` |
| Verifying completion, refactoring or preparing delivery | `references/verification.md` |
| Reviewing a diff or folding findings | `references/defect-classes.md`, then `references/review.md` |
| PR slicing, migrations, gates, commits or merge | `references/workflow.md` |
| Runtime startup, deployment or recovery | `references/delivery.md` |
| Latency or throughput target, slow query, load, cache or scale claim | `references/performance.md` |
| Delegating independent work or coordinating agents | `references/orchestration.md` |
| Working with agents: asking vs proceeding, reviewing agent diffs, instruction files | `references/agent-collaboration.md` |

Evidence and its limits live in the repository's `EVIDENCE.md`; do not load it for routine coding. This skill aims to improve decision coverage; correctness still requires execution and independent review.
