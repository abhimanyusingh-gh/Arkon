# Getting started

`craft` is a Claude Code skill. This page covers installing it, using it, adapting it to a project, and what changed in 1.3.0.

## Install

As a plugin, which gives you versioning and updates:

```
/plugin marketplace add abhimanyusingh-gh/Arkon
/plugin install craft@Arkon
```

Or symlink it directly, if you'd rather track `main` and edit in place:

```bash
git clone https://github.com/abhimanyusingh-gh/Arkon.git
mkdir -p ~/.claude/skills
ln -s "$(pwd)/Arkon/skills/craft" ~/.claude/skills/craft
```

For a single project, copy `skills/craft/` into `<project>/.claude/skills/craft/` and commit the skill files so the team receives the same version.

If you added the marketplace under its earlier name, `software-craftsmanship`, add it again as `abhimanyusingh-gh/Arkon`.

## Use it

Claude invokes the skill on its own when a task matches its description; `/craft` invokes it explicitly. You can also ask directly, for example "Use craft to review this diff against its acceptance criteria". The skill loads its core rules and an evidence card, then reads each reference when the work reaches that boundary. See the [reference guide](04-REFERENCE_GUIDE.md) for the routing.

Two mechanisms keep the work reviewable:

- **Workers read the relevant guidance** before implementation. A brief points to the skill and the owned boundaries; substantial handoffs use the evidence card.
- **Substantial work returns a filled-in evidence card; small fixes can report evidence in prose.** State acceptance criteria, affected boundaries and deliberate omissions, and back verification claims with commands and actual results. "All tests pass" is not a result; `1331/1331, 10 skipped` is. An unavailable gate is reported by name and reason.

The plugin checks for updates at session start and reminds you when a new version exists (at most once a day, never blocking). Run `python3 scripts/check_skill_version.py` to check by hand.

## Adapt it to a project

**Bind the project.** Derive commands, datastore behavior, framework conventions, customer scope and application composition from the repository and CI. The discovery script writes a starting point with a confidence level per field:

```bash
python3 skills/craft/scripts/discover_project_context.py . --out .claude/craft-context.json
```

Treat its output as evidence to verify, not as authority ([`project-binding.md`](../skills/craft/references/project-binding.md)). Use the language's native types and the actual dependency versions; stack-specific examples are conditional guidance, not instructions to introduce a different toolchain. Using the skill does not require rewriting agent instructions.

**Calibrate requirements.** Scope isolation and lost-capability checks address concrete failure modes. Style preferences, complexity thresholds and deployment mechanisms depend on context. Apply severity to the demonstrated consequence, and record why a control is inapplicable.

**Use history as evidence.** Follow [`history.md`](../skills/craft/references/history.md) to inspect authored commits and their actual diffs, and separate independent incidents from rework sequences. [`EVIDENCE.md`](EVIDENCE.md) records reversals and the limits of the original audit. Evaluate proposed changes on held-out cases with the [evaluation protocol](evaluation.md).

## What's new in 1.3.0

- Project-binding discovery script and reference (`project-binding.md`), also packaged as the standalone `arkon-discover` command (ready for PyPI, not yet published).
- Rationalization tables in `verification.md` and `review.md` that answer common excuses with the rule they break.
- `TRIFECTA-BOUNDARY` and `INJECTION-BOUNDARY`, and an OWASP Top 10 (2021) and OWASP Top 10 for LLM Applications (2025) coverage map, in `security.md`.
- Property-based testing guidance (`PBT-PROPERTY`, `PBT-REPRO`) in `testing.md`.
- Agent-collaboration reference: when to ask versus proceed, reviewing agent-authored diffs, instruction-file boundaries.
- Mechanical rule checks for deleted tests, added skips and empty catch blocks (`check_rules.py`).
- Performance reference: measurement, query, budget and cache rules.
- `LLM-COST` and `LLM-EVAL` in `llm-calls.md`, and `REVIEW-SPEC` spec-conformance review in `review.md`.
- Line caps and rule-ID resolution enforced by `scripts/validate_skill.py` in CI.
- [Methodology](03-METHODOLOGY.md): how the evidence was collected, counted and limited.
- Update reminder at session start; the marketplace is now `Arkon`.
