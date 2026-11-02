# Tickets, wiki pages and design docs

Use for work items, stories, wiki pages, and design or decision docs. Docs that ship with code follow the same-commit rule in `workflow.md`.

## DOC-TICKET — stories are small, objective and re-readable

- A story states the outcome and the observable behavior it needs. Leave out implementation detail such as file names, classes, schemas and libraries; those belong in the design or the PR.
- Give at most three acceptance criteria, each objective: a command result, a response, a visible state. Replace a vague criterion with a measurable one or drop it.
- Prefer a few small stories that each yield a demonstrable slice over many tiny stories that each pass one layer.
- An initiative names one data-backed, non-code metric with its source, baseline and re-read cadence. Key results build on that metric; they do not sit beside it. A delivery count or build status is not an outcome metric.

## DOC-WRITE — docs are short, verified and easy to act on

- Lead with the current state, then the target state, then one small first step that a reader can act on without reading the rest.
- Cut filler: preambles, hedges, and summaries that repeat the body. Use plain sentences.
- Assert only what you verified in this session or can cite (a file path, a log line, a ticket). Mark everything else as an open question.
- State each number once, with its unit and source. Refer to it elsewhere instead of copying it, so one edit updates every use.
- Before publishing, run an edit pass for AI-sounding phrasing: generic openers, stacked adjectives, "robust", "seamless", reflexive triads, and sentences that restate the one before. Rewrite them plainly.
- Remove placeholder text and unticked template boxes. A section that does not apply says so in one line.
- For a long doc, agree the idea and scope with the user first. Diagrams are welcome where they show a flow or a boundary; a diagram that repeats the text adds noise.
- Link tickets and PRs by key or title. Do not print raw commit SHAs in prose.
- Re-check the doc against the code it describes with the documentation check in [defect-classes.md](defect-classes.md).
- End with an explicit invitation to comment on the open decisions.

## DOC-DELEGATE — the orchestrator plans, the cheap tier moves the records

- Tracker and wiki reads and writes go to the cheap tier named in [orchestration.md](orchestration.md). The orchestrating session plans, drafts and decides.
- Draft the exact text and show it before any external write. Post or edit only after approval, as `ORCH-EXTERNAL-WRITE` in [orchestration.md](orchestration.md) requires.
- Re-read the object after writing and compare it with the draft. The write counts as done only when the re-read matches.
- Set a version message on each wiki edit that says what changed and why.
- Refer to other tickets and pages by stable link, not by a pasted copy that will drift.
