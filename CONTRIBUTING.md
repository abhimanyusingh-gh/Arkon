# Contributing

Thanks for helping improve `craft`. Changes land through pull requests; `main` is protected and merges are squash merges.

## Before you open a pull request

Run the same gates as CI, from the repository root:

```bash
python3 -B scripts/validate_skill.py
python3 -B -m unittest discover -s tests -v
git diff --check origin/main HEAD
```

CI runs them on Python 3.9 and 3.12. Report the actual output in the pull request, including skips. The pre-release checks in [`docs/publish-checklist.md`](docs/publish-checklist.md) apply to any change that alters guidance.

## Changing guidance

- **Route every reference.** A new file under `skills/craft/references/` needs a trigger row in `SKILL.md`, which must stay at or under 110 lines.
- **Define rule IDs once,** as `**ID — summary.**` or `## ID — summary`, and cite them by ID elsewhere. The validator resolves IDs cited in the verification and review tables.
- **Respect the line caps** that the validator enforces on long references; split a guide only when it improves routing.
- **Label the evidence.** Add provenance to [`docs/EVIDENCE.md`](docs/EVIDENCE.md) as observed findings, reported evidence, operating experience, engineering judgment, or external and unreproduced. Do not invent counts, and record counterexamples that change a rule.
- **Keep runtime files clean.** No private names, internal ticket IDs, absolute paths, secrets or copied source in `skills/`.
- **Keep it stack-neutral.** Label framework-specific syntax as an example rather than a requirement.

## Changing scripts

Helpers are Python 3.9+, standard library only, with tests in `tests/` that use temporary directories or repositories. Scripts must not make network calls unless that is their purpose (the update reminder) and must never block a session.

## Commits and versions

Write commit subjects that describe the diff. Bump `version` in `.claude-plugin/plugin.json` and `pyproject.toml` together; merging a new version to `main` publishes a GitHub release.
