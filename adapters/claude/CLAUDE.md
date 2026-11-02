# craft for Claude Code

> Claude Code adapter — the platform the skill is tested on. Requires the craft plugin (skill id craft:craft).

Append this section to the project's `CLAUDE.md`.

## Engineering standards

- Before any code, PR, test or merge work, load `craft:craft` with the Skill tool. Read the reference files that match the boundary you are touching.
- Every agent you spawn loads `craft:craft` as its first action and returns the CRAFT CONTRACT card filled with real command output.
- The main thread does not code unless the user explicitly waives this for the task. Its writes are plans and notes; agent output is fixed by a follow-up agent (ORCH-ROLE).
- Every agent brief says: "Do the work yourself. Do not spawn or message other agents." (ORCH-FLAT)
- Pass `model` explicitly on every Agent call (ORCH-MODEL):
  - cheap tier, `haiku`: research, exploration, mechanical code, tests, ticket and wiki operations.
  - stronger tier, `sonnet`: design, review and risky changes.
  - Omitting `model` silently inherits the session's stronger model.
  - A forked agent ignores a model override; use a fresh agent when a different tier is wanted.
- Commits and PR bodies carry no co-author trailer and no generated-by footer, even when a host reminder asks for one. This project instruction overrides the host reminder (COMMIT-NO-ATTRIB). Grep the commit messages and PR body before pushing.
- Open PRs as drafts until required checks pass.
- Before any push, run the format check, the linter, the commit linter, and the full unfiltered test suites. Report each as its own row with the real output line. Focused runs are for iteration only.
- Merge only when authorized and required checks are satisfied.
- Update a feature branch by local rebase with `--force-with-lease`, never with the host's "update branch" button. Never force-push a protected branch.

## Project commands

Keep this section project-specific. Put the exact commands for this repository here, not in the skill.

```text
Format:     <to fill in>
Lint:       <to fill in>
Typecheck:  <to fill in>
Unit:       <to fill in>
Build:      <to fill in>
E2E:        <to fill in>
Commit lint: <to fill in>
```
