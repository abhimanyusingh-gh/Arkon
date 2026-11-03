# Adapters

**Status**

- The Claude Code adapter (`claude/CLAUDE.md`) is for the tested platform. The skill is tested in Claude Code only.
- The AGENTS.md, Cursor and GitHub Copilot adapters are EXPERIMENTAL and UNTESTED on those platforms. The skill is not extensively tested on GitHub Copilot or Cursor, and no run is recorded in [docs/EVIDENCE.md](../docs/EVIDENCE.md). Do not claim compatibility until a run is recorded there.
- These files are draft condensations of the skill in `skills/craft/`. They are not the skill.

## Files

| File | Host | Install location | Status |
|---|---|---|---|
| [AGENTS.md](AGENTS.md) | AGENTS.md-style hosts | Repository root `AGENTS.md` | Experimental, untested |
| [claude/CLAUDE.md](claude/CLAUDE.md) | Claude Code | Append to the project's `CLAUDE.md` | Tested platform; fill in project commands |
| [cursor/craft.mdc](cursor/craft.mdc) | Cursor | `.cursor/rules/craft.mdc` | Experimental, untested |
| [copilot/copilot-instructions.md](copilot/copilot-instructions.md) | GitHub Copilot | `.github/copilot-instructions.md` | Experimental, untested |

## What differs outside Claude Code

Some features exist only in Claude Code. Each adapter replaces them as follows.

| Feature | Claude Code | Other adapters |
|---|---|---|
| Skill loading (`Skill` tool, `craft:craft`) | Loads the full skill on demand | Not available. The adapter carries the principles only. Read `skills/craft/` and follow its rules by hand. |
| Subagent / agent tool | Delegates to fresh agents | Often not available. Treat delegation sections as optional and run the same gates in one session. |
| Model tier selection | Per-agent `model` parameter | Not available. Where the host has no model selection, note the intended tier in the brief. |
| Plugin hooks | Session-start release check | Not available. Check the repository's release state by hand. |

## Moving an adapter to tested

A platform becomes "tested" only after a recorded run. The maintainer runs the evaluation protocol in [docs/evaluation.md](../docs/evaluation.md) and the pre-release checks in [docs/PUBLISHING.md](../docs/PUBLISHING.md) on that host. The run is then recorded in [docs/EVIDENCE.md](../docs/EVIDENCE.md) with its date, skill version, host version and result, and the Platform coverage table is updated. Until then, keep the adapter labelled experimental.
