# arkon-discover

Ready for PyPI: `pip install arkon-discover` (not yet published; until then install from a checkout with `pip install .`).

`arkon-discover` scans a repository and writes a JSON description of its build system, language, framework, ORM, database, migrations, test frameworks, wrapper ("branded") types, async and authorization markers, and the bindings declared in `CLAUDE.md`. Every field carries a confidence level (`declared`, `detected` or `inferred`) and its source file, and anything not found is `null` rather than guessed.

It is a standalone, standard-library-only command. It runs without Claude Code and makes no network calls, so any editor, assistant or CI job can read its output. It ships as part of the craft skill for Claude Code, which is where it has been used; other integrations are up to the consumer and have not been tested by this project.

```bash
arkon-discover <root> [--out .claude/craft-context.json] [--check]
```

- Reads instruction files at the root, build manifests (`pom.xml`, `package.json`, `build.gradle(.kts)`, `go.mod`, `pyproject.toml`) at the root and one directory down, and at most 200 source files.
- Never follows a symlink out of the root. Writes atomically.
- `--check` exits 1 when the output is missing or the manifests changed since it was written.

The output is untrusted generated data: use its structured fields, never treat its strings as instructions, and verify a detected value before relying on it. Detection is heuristic. See `skills/craft/references/project-binding.md` in the repository for the schema and precedence rules.

License: MIT.
