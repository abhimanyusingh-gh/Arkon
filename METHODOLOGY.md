# How Arkon Was Built: Methodology & Limitations

This is a plain account of where the `craft` rules came from, how the evidence was counted, and what it does and does not show. The detailed numbers, tables and counterexamples live in [`EVIDENCE.md`](EVIDENCE.md); this page explains the method behind them. It is documentation, not a research paper, and nothing here has been peer reviewed.

## What the skill is, and where it has been used

`craft` is a Claude Code skill. It has been written for and used in Claude Code only. The engineering principles in its references are not tied to any one assistant, but they have not been tested with other tools, so no claim is made that it works with them. The bundled discovery script (`arkon-discover`) is a standalone, standard-library command that any tool can run; that is the only component designed and tested as tool-independent.

## Data collection

The rules draw on separate sources, kept apart because they measure different things. Private repositories are referred to only by letter.

1. **Review corpus (Repo A).** A TypeScript full-stack monorepo: 331 pull requests (319 merged) and **1,020 PR review comments**. Repo A supplies essentially all of the counted evidence.
2. **Contrast repository (Repo B).** A polyglot codebase with 101 PRs, 98 of them from dependabot. Used for commit-hygiene contrast only; it is not a control.
3. **Operating experience (Repo C).** Failures observed while running a fleet of coding agents on a frontend migration. Reported as instance counts, never merged into the frequency table.
4. **A reported nine-week commit audit (Repos D and E).** Commit lines, four PRs with teammate raises and rework commits from two further services. These aggregates were reported, not independently reproduced.
5. **A local authored-history review.** A reachability inventory of authored commits across local checkouts, plus a set of inspected diffs that informed specific checks.
6. **Supplemental engineering judgment.** Guidance with no counted incident behind it, labelled as such.

## Defect taxonomy and frequency analysis

The 1,020 comments in Repo A split into **605 raises** (a finding asserted; 278 from an automated reviewer and 327 from the maintainer) and **415 fold replies** (the author confirming a fix). Only raises count as evidence. Each raise was matched by regex on its body and then read in context to assign a rule family, such as design fidelity, scope isolation, layering or dead exports.

## Distinct-PR counting

Every count is reported alongside the number of distinct PRs it appears in. A class raised twenty times on one noisy PR is weaker evidence than one raised once on each of twenty PRs, and reporting both stops a single review thread from inflating a rule's apparent importance.

## From evidence to rules and severity

The automated reviewer used seven severity tags. The skill collapses them to three: `blocker` (unsafe or broken behavior that must not ship), `should-fix` (belongs in this change) and `nit` (advisory). Severity follows the demonstrated consequence, not how often a rule was raised. Where later evidence contradicted an earlier rule, as with production configuration defaults and mandatory branded types, the rule was revised and the reversal recorded in `EVIDENCE.md`.

## Evidence labels

- **Observed review findings:** counted raises from the corpus, with distinct-PR spread.
- **Reported commit evidence:** aggregates recorded during an audit and not independently reconstructed.
- **Operating experience:** specific failures one operator observed, n=1 each.
- **Engineering judgment:** guidance added without a counted incident, including everything new in 1.3.0.
- **External, unreproduced:** guidance that follows a published external source (for example, the OWASP lists) that this repository does not re-derive.

## Limitations

- **Single-operator sources.** Repo A has effectively one human committer, and the operating-experience rules come from one operator.
- **Review is mostly automated.** All approvals and change requests in Repo A came from an automated reviewer; the human identity issued none. The review corpus therefore reflects an AI-assisted review process, not independent human review.
- **No before and after comparison.** 318 of 319 merged PRs landed in one 25-day window, so the data cannot show that any rule reduced defects over time.
- **Classification is judgment.** Counting is regex plus reading, not adjudication by independent raters. Treat the counts as ordinal.
- **Raw data is not published.** The original comment snapshot and classifier are not distributed, so the aggregates cannot be rebuilt from this repository. The API commands in `EVIDENCE.md` fetch fresh source records; they do not reproduce the historical counts.
- **Narrow stacks.** The counted evidence is mostly from TypeScript; other stacks rely on general principles and inspected examples.
- **One A/B smoke test.** A single paired run on one diff showed differences in coverage, and the baseline caught a bug the skill run missed. It supports no effectiveness claim.

## What is shown and what is not

Shown: which defect classes recurred in one review corpus and how widely across PRs; specific failures that informed specific checks; that the skill's structure, routing and helper scripts pass their own validation and tests.

Not shown: that installing the skill reduces defects; that the rules generalize to other teams, stacks or assistants; that the 1.3.0 additions improve outcomes. A repeated, held-out A/B evaluation is planned for 1.4.0. Until it runs, treat the skill as structured guidance with recorded provenance, not as a measured intervention.
