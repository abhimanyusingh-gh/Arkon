# Publishing checklist

Steps for the maintainer to run with their own accounts. Nothing here has been published by automation; every external post or upload is a deliberate maintainer action. Run the pre-release checks in [`docs/publish-checklist.md`](docs/publish-checklist.md) first.

## Messaging rules

Use these in every channel.

- **Claude Code skill:** "Engineering standards for Claude Code." The full feature set (skill, references, hooks, update reminder) is built for and tested in Claude Code.
- **Discovery script:** "`arkon-discover` is a standalone, stdlib-only command that works with any IDE or tool." This is the only component designed and tested as tool-independent.
- **Engineering references:** "Tool-agnostic principles, tested only in Claude Code."
- **Evidence:** "Derived from 1,020 review comments in one codebase plus inspected history and operating experience; see METHODOLOGY.md for the limits." Never say the skill is proven to reduce defects.
- **Do not claim** compatibility with GitHub Copilot, Cursor, Devin or any other assistant until it has been tested there and the test is recorded in `EVIDENCE.md`.

## 1. PyPI (`arkon-discover`)

- [ ] Confirm the name is free: `pip index versions arkon-discover` (or check https://pypi.org/project/arkon-discover/).
- [ ] Build in a clean venv: `python3 -m venv /tmp/arkon && /tmp/arkon/bin/pip install build twine && /tmp/arkon/bin/python -m build`.
- [ ] Check the artifacts: `/tmp/arkon/bin/twine check dist/*`; install the wheel in a fresh venv and run `arkon-discover --help`.
- [ ] Upload to TestPyPI first with your account token: `twine upload --repository testpypi dist/*`, then `pip install -i https://test.pypi.org/simple/ arkon-discover`.
- [ ] Upload to PyPI: `twine upload dist/*`. Prefer a scoped API token or trusted publishing; never commit a token.
- [ ] Remove "not yet published" from `packaging/README.md` and the README's 1.3.0 list in a follow-up PR.

## 2. GitHub release

- [x] v1.3.0 was published by the release workflow on merge.
- [ ] Optionally replace the generated notes with:

```text
v1.3.0

Claude Code skill: project-binding discovery, OWASP coverage map, TRIFECTA and
injection boundaries, agent-collaboration, performance, LLM cost and evaluation,
spec-conformance review, property-based testing, mechanical rule checks, and a
session-start update reminder. The marketplace is now Arkon:
/plugin install craft@Arkon

Standalone: arkon-discover, a stdlib-only project-context detector that runs
with any IDE or tool (PyPI release pending).

Tested in Claude Code only. Methodology and limits: METHODOLOGY.md.
```

## 3. Blog post (Dev.to, Medium, personal blog)

- [ ] Title: "Engineering standards for Claude Code, with the evidence behind each rule".
- [ ] Outline: the problem (agents pass gates while losing behavior), how rules were derived (link METHODOLOGY.md), three examples from the README, what is not proven, how to install, the standalone discovery script.
- [ ] Publish on one platform first; cross-post with a canonical URL.

## 4. Social and forums

- [ ] **LinkedIn / X:** "Arkon 1.3.0: engineering standards for Claude Code, each rule traced to review evidence or labelled as judgment. Includes arkon-discover, a standalone project-context detector for any tool. Limits documented: <link to METHODOLOGY.md>"
- [ ] **Hacker News (Show HN):** "Show HN: Arkon – evidence-labelled engineering standards for Claude Code". First comment: what it is, how the evidence was counted, the single-operator and automated-review limitations.
- [ ] **Discord:** a short post with the install command and the methodology link.

## 5. Communities

- [ ] Anthropic / Claude Code community channels: the full skill.
- [ ] GitHub Copilot and Cursor communities: only `arkon-discover`, framed as a standalone detector whose JSON any tool can read. Do not present the skill as supported there.
- [ ] Engineering, SRE and DevOps communities: the methodology and the evidence-labelling approach.

## Timing

1. PyPI (TestPyPI, then PyPI), then update the package README.
2. GitHub release notes.
3. Blog post.
4. LinkedIn, X and Discord the same day as the post.
5. Show HN on a weekday morning (US Eastern), when you can answer comments for several hours.
6. Community posts over the following week, one at a time, responding to feedback before the next.
