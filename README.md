# Arkon

Arkon publishes `craft`, a skill for [Claude Code](https://claude.com/claude-code): engineering guidance for building, changing and reviewing production applications. It defines acceptance criteria, designs boundaries, implements complete slices, reviews behavior, verifies the real application and prepares a recoverable release, on any stack. Each rule is traced to review evidence or labelled as judgment. The skill was built for and is tested in Claude Code. The engineering principles do not depend on Claude Code, but they have not been tested anywhere else. The project-binding discovery script also runs on its own and works with any IDE.

## Install

```
/plugin marketplace add abhimanyusingh-gh/Arkon
/plugin install craft@Arkon
```

Then ask Claude to "use craft" on a task, or type `/craft`. Other install options are in [Getting started](docs/01-GETTING_STARTED.md#install).

## Documentation

- [Getting started](docs/01-GETTING_STARTED.md): install, use, adapt to a project, and what's new in 1.3.0
- [Examples](docs/02-EXAMPLES.md): anonymized production excerpts and the TRIFECTA-BOUNDARY threat model
- [Methodology](docs/03-METHODOLOGY.md): how the evidence was collected and counted, and its limits
- [Reference guide](docs/04-REFERENCE_GUIDE.md): all references, when each loads, and the helper scripts
- [Architecture](docs/ARCHITECTURE.md): repository layout, how the skill loads, validation and release
- [Evidence](docs/EVIDENCE.md): findings, counts, counterexamples and caveats behind the rules
- [Evaluation](docs/evaluation.md): the behavioral evaluation protocol
- [Contributing](CONTRIBUTING.md): gates and conventions for changes
- [Publishing checklist](docs/PUBLISHING.md): maintainer steps for releases and announcements

## Key features

- **Progressive references.** 22 boundary guides load only when a task reaches that boundary. They cover security, tenancy, async jobs, LLM calls, performance, testing, verification and review.
- **An evidence card.** Substantial work reports acceptance, scope, safety, gates and anything not run. "All tests pass" is not evidence.
- **Security for AI-assisted work.** The guides cover the private-data, untrusted-content and outbound-effect trifecta, prompt injection, and an OWASP coverage map.
- **Mechanical checks.** Bundled scripts flag deleted tests, added skips and empty catch blocks, and discover a project's bindings with a confidence level per field.
- **Recorded provenance.** Every rule's source and limits are documented. The skill does not claim a measured defect reduction.

## License

MIT
