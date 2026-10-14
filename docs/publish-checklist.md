# Publish checklist

Run these checks before releasing a changed skill. Local validation and a commit do not authorize a plugin install, remote publication, deployment, or changes to branch protection.

## Package and helper checks

From the repository root:

```bash
python3 -B scripts/validate_skill.py
python3 -B -m unittest discover -s tests -v
claude plugin validate . --strict
git diff --check
```

The stdlib validator checks frontmatter, reference triggers, sibling links, Markdown fences, JSON examples, helper syntax, and manifests. It cannot establish instruction quality or application correctness. The unit suite uses disposable repositories to check inventory attribution, scope, deduplication, patch equivalence, and coverage reporting. Run under the supported Python versions, including the local runtime.

Review both the working diff and the actual committed base/head range before publishing. A clean checkout's bare `git diff --check` checks no committed changes. The CI workflow checks the event's base against its head; release creation waits for validation.

## Guidance and provenance

- Read each changed rule against its counterexamples and existing authoritative statements. Remove or revise an old instruction when evidence reverses it; do not leave opposing mandates in two guides.
- Check that every new guide has a precise trigger in `SKILL.md`, every trigger resolves, and reviewer guidance covers the new failure class. Load references as needed rather than imposing a fixed read count.
- Keep the entrypoint within about 110 lines. Split a guide only when it improves routing; reference length is a maintainability signal, not a reason to discard a useful invariant.
- Keep runtime guidance stack-neutral. Label concrete toolchain/provider syntax as an example; do not turn one framework's API into a requirement for another.
- Inspect runtime files for private names, internal ticket IDs, absolute workspace paths, copied source, secrets and real payloads. Keep source provenance separate from runtime instructions; publish only approved, minimized metadata.
- Map evidence labels to the canonical current rule IDs. Distinguish independently observed findings, correlated rework, operating experience, preferences, and supplemental engineering judgment. Do not invent a finding count for an unmeasured recommendation.

Useful inspection searches, read in context:

```bash
rg -n '/Users/|/home/|~/' skills/
rg -n '\b[A-Z]{2,6}-[0-9]+\b' skills/
rg -n 'always|never|must|only|every' skills/craft/
rg -n 'references/|scripts/' skills/craft/SKILL.md
```

A hit is a lead. Platform terminology, synthetic examples, and invariant-driven safety requirements are legitimate; check whether a literal is local residue or a reusable constraint.

## Behavior, scope, and evidence

Use [the evaluation protocol](evaluation.md), which records misses and false positives as well as successes. At least exercise the changed decision on a realistic fixture. A substantial revision benefits from a fresh evaluating agent that receives the request, skill, and raw artifacts without the suspected bug or reference answer.

Verify:
- The agent connects the primary journey through real composition instead of stopping at scaffolded layers.
- Authorization, concurrency and recovery are enforced by the actual boundary, with the relevant negative cases.
- An intentional product-contract change updates tests meaningfully, while a behavior-preserving change retains its guarantees.
- Small tasks stay small, and the skill does not invent authorization, mandatory fleets, instruction-file edits, tracker actions, remote pushes, or deployments.
- Reported gates identify their tested revision and completion. Skipped, pending and blocked checks remain visible limitations.
- Different stacks keep their own types, framework patterns and commands.

Record the exact task, fixture/skill revision, actual edits/commands, misses, false positives, and remaining limitations. An explicit-invocation smoke does not prove automatic skill discovery. A single run is not a benchmark or evidence of a lower production defect rate.

For a release install check, use an authorized disposable environment to load `/craft` and resolve a reference plus the bundled helper. Do not change a user's global plugin installation as an incidental validation step.

## Version and release

Bump `version` in `.claude-plugin/plugin.json` for a release-worthy change; it is the authoritative version. Keep name/description aligned with `.claude-plugin/marketplace.json`. Validate first; follow the repository's release process only when publishing is authorized.

## Repository conventions

`main` requires a pull request from everyone, including admins. Zero approvals are required, so the merge action is the approval. Force pushes and branch deletion are blocked. Do not weaken this to make an automated workflow easier.

Platform squash merges may use the platform's committer identity. That is accepted. Do not rewrite history or bypass branch protection for cosmetic identity consistency. Author local commits under the configured repository identity; do not add assistant attribution or co-author trailers.
