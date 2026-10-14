# software-craftsmanship

Skills for [Claude Code](https://claude.com/claude-code).

## craft

Engineering guidance for developing and maintaining production applications: define acceptance criteria, design boundaries, implement complete slices, review behavior, verify the real application, and prepare a recoverable release. It applies across stacks and includes guidance for agent fleets.

The skill combines a reported corpus of 1,020 review comments, inspected local authored history, operating experience, and supplemental engineering judgment. [`EVIDENCE.md`](EVIDENCE.md) separates those sources, records counterexamples and unresolved counting limitations, and avoids treating commits or test classes as independent defects. It does not establish that installing the skill reduces defects.

Use the lifecycle mode that matches the work: design, implement, review, verify, deliver, or learn from history. Define observable acceptance criteria before coding; include authorization, data consistency, integration failure, and deployment behavior when the change touches them. Review and verification follow the changed behavior through real consumers and dependencies.

Claude loads the core rules and a contract card, then follows the relevant reference triggers. A complex production change may need several guides; coverage follows the risk and dependencies of the task.

| Reference | Covers |
|---|---|
| `application-design.md` | acceptance criteria, complete vertical slices, application boundaries, temporal data selection, and cross-field consistency |
| `security.md` | authorization boundaries, untrusted input, secrets, and safe persisted results |
| `tenancy.md` | scope isolation — every read, write, aggregate, storage path and cache key scoped; enforcement at the lowest layer; the negative test |
| `authoring.md` | reuse, layering, dead code vs unwired capability, native domain types, naming, complexity, fail-closed configuration, database locking, and query plans |
| `integrations.md` | external-call budgets, idempotency, asynchronous identity, and consistency across boundaries |
| `async-jobs.md` | distributed execution, leases, claims and fencing, retirement, and real-database concurrency checks |
| `observability.md` | safe logs and error responses, useful correlation, and content-leak sentinel tests |
| `llm-calls.md` | model-call tracing, untrusted output validation, minimal prompts, and failure handling |
| `dependencies.md` | advisory-driven remediation, dependency overrides, transitive changes, and real-application boot checks |
| `frontend.md` | design fidelity, server/local state, inactive drafts, stale responses, AI preview acceptance, accessible errors, and bulk-operation partial failure |
| `accessibility.md` | disabled-vs-aria-disabled, one interaction model per widget, announce-after-settle, focus and reduced motion, the per-PR baseline |
| `testing.md` | invariants and negative tests, characterization and concurrency tests, seed data, meaningful test updates, and unit-to-browser execution |
| `verification.md` | proving a claim rather than making one — gate evidence, the base-vs-branch regression diff, green-by-deletion, harness masking, selector inventories, the browser-spec pass |
| `defect-classes.md` | the reviewer's entry point — historical defect shapes and affected production boundaries, with severity tied to the consequence |
| `review.md` | root-cause reproduction, correctness review, folding findings, full-PR re-review, and escalation when defect patterns recur |
| `workflow.md` | work intake, PR slicing, immutable and rolling-compatible migrations, gates, truthful commit subjects, merge policy, and docs currency |
| `delivery.md` | deployed compatibility, release readiness, rollout, recovery, and post-deploy verification |
| `orchestration.md` | bounded delegation, shared-state ownership, isolation, integration review, resource limits, and resumable handoffs |
| `history.md` | attributable history discovery, inspecting base/fix evidence, separating repeated patches from incidents, and calibrating proposed rules |

Progressive disclosure keeps specialized guidance out of unrelated tasks. The author and reviewer read additional guides when they discover another affected boundary; there is no fixed three-reference ceiling.

## Keeping agents on it

Two mechanisms in `SKILL.md` make the work reviewable:

- **Workers read the relevant guidance** before implementation. The brief points to the skill and owned boundaries; use the contract card for substantial handoffs.
- **Substantial work returns a filled-in contract card; small fixes can report evidence in prose.** State acceptance criteria, affected boundaries, and deliberate omissions; back verification claims with commands and actual results. "All tests pass" is not a result, `1331/1331, 10 skipped` is. An unavailable gate is reported by name and reason. `verification.md` checks for lost behavior, deleted coverage, and harnesses that hide failures in the real application.

## Install

As a plugin, which gives you versioning and updates:

```
/plugin marketplace add abhimanyusingh-gh/software-craftsmanship
/plugin install craft@software-craftsmanship
```

Or symlink it directly, if you'd rather track `main` and edit in place:

```bash
git clone https://github.com/abhimanyusingh-gh/software-craftsmanship.git
mkdir -p ~/.claude/skills
ln -s "$(pwd)/software-craftsmanship/skills/craft" ~/.claude/skills/craft
```

For a single project, copy `skills/craft/` into `<project>/.claude/skills/craft/` and commit the skill files so the team receives the same version.

Claude invokes the skill on its own when a task matches the description; `/craft` invokes it explicitly.

## Adapting it

**Bind the project.** Derive commands, datastore behavior, framework conventions, customer scope, and application composition from the repository and CI. Use the language's native types and the actual dependency versions. Stack-specific examples are conditional guidance, not instructions to introduce a different toolchain. Keep bindings in working notes or an existing project-approved location; using the skill does not require rewriting agent instructions.

**Calibrate requirements.** Scope isolation and lost-capability checks address concrete failure modes. Style preferences, complexity thresholds, and deployment mechanisms depend on context. Apply severity to the demonstrated consequence, and record why a control is inapplicable. An intentional acceptance-contract change can require a test update; maintain behavioral coverage and show the changed requirement.

**Use history as evidence.** Follow `history.md` to inspect available authored commits and their actual diffs, state what history is missing, and separate independent incidents from rework sequences. [`EVIDENCE.md`](EVIDENCE.md) records reversals on defaults, branding, and immutable assertions, plus the limits of the original audit. Evaluate proposed changes on held-out cases and measure missed defects and false positives alongside useful findings.

The bundled read-only inventory helper accepts explicit roots and author patterns; see [history guidance](skills/craft/references/history.md). Maintainers can run `python3 -B scripts/validate_skill.py` and `python3 -B -m unittest discover -s tests -v`. [Behavioral evaluation](docs/evaluation.md) includes a runnable application fixture, a recorded development smoke, and checks for missed defects and false positives; structural validation alone does not prove coding quality.

## License

MIT
