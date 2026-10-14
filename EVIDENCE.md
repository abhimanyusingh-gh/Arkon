# Evidence

This file separates review findings, inspected commit history, operating experience, and engineering judgment. It is the audit trail for deciding which rules to keep when adapting the skill. A rule's presence here is not proof that it reduced defects.

It lives outside `skills/` so routine tasks do not load the full research history. History-driven changes should consult it: evidence strength and counterexamples affect how a rule should be applied.

## Corpus

The original review audit covered three private production codebases, referred to here only as Repo A, Repo B and Repo C. The later commit-history audits below are separate sources; the repository aliases do not establish that the corpora are independent.

| | Repo A | Repo B | Repo C |
|---|---|---|---|
| Stack | TypeScript full-stack monorepo | polyglot — Kotlin, TypeScript, SCSS, Gherkin | TypeScript frontend |
| Commits on the default branch | 1,679 | 813 | — |
| Pull requests | 331 (319 merged) | 101, of which **98 are dependabot** | — |
| Issues | 315 (262 closed) | 0 | — |
| PR review comments | **1,020** | 0 (dependabot comments only) | not counted |

Repo A supplies essentially all of the counted evidence. Repo B is included for commit-hygiene contrast only — see the caveats below for why it is not a control.

**Repo C is a different kind of source and is kept separate deliberately.** No comment corpus was extracted from it. It contributes a handful of rules that came from watching an agent fleet fail in specific, reproducible ways during a design-system migration — reported as instance counts in their own table below, never merged into the frequency table above. Treat them as operating experience, which is what they are.

## Method

The 1,020 comments in Repo A split into two kinds, and only one kind is evidence:

- **605 raises** — a finding being asserted (278 from an automated reviewer, 327 from the maintainer).
- **415 fold replies** — the author confirming a fix (opening with "Addressed", "Fixed", "Round N", or citing a commit).

Counts below are **raises only**, de-duplicated per comment, matched by regex on the body and read in context. **Distinct-PR spread is reported alongside every count**, because a class flagged 20× on one PR is not the same evidence as one flagged 20× across 20 PRs.

The automated reviewer tagged its own severity on 254 findings: `NIT` 121, `SHOULD-FIX` 85, `QUESTION` 21, `INFO` 11, `BLOCKER` 10, `CRITICAL` 5, `MUST-FIX` 1. That distribution is why this skill uses a three-level vocabulary rather than seven.

## Original rule-family signals

This table preserves the original audit's reported counts and policy labels. It is not the current normative rule set: later revisions qualify stack-specific preferences, file budgets, immutable assertions, and deployment assumptions. The runtime references are authoritative for current behavior.

| Rule family | Rule IDs | Findings | Distinct PRs |
|---|---|---|---|
| Design fidelity, tokens, design completeness | `frontend.md` fidelity | **70** | 48 |
| Full unfiltered gates before push | `workflow.md` gates | **62** | 40 |
| Code reuse and duplication | `REUSE-*` | **43** | not validated; reported 51 |
| Scope isolation | `SCOPE-*` | **41+** | 25+ |
| Layering | `LAYER-*` | **34** | 27 |
| Docs ship with the change | `workflow.md` docs | **29** | 11–27 |
| Dead exports | `DEAD-EXPORT` | **26** | 22 |
| Seed data coverage, idempotency, modes | `SEED-MODE` | **24** | 17 |
| Const-as-enum over literals | `ENUM-*` | **23** | 18 |
| Complexity limits | `authoring.md` complexity | **23** | 19 |
| Naming and test-id taxonomy | `NAME-*`, `TESTID-*` | **18** | 15 |
| Invariant tests over happy-path | `testing.md` invariants | **18** | 12 |
| Accessibility | `A11Y-*` | **17** | 14 |
| Server state through the cache library | `frontend.md` state | **16** | 10 |
| E2E rules | `testing.md` e2e | 14 | 10 |
| Config from day one | `CONFIG-*` | 12 | 11 |
| URL provider abstraction | `URL-*` | 11 | 8 |
| Cross-PR contract drift, dead cache keys | `MIGRATE-*` | 10 | 10 |
| No narrative comments | `authoring.md` style | 10 | 9 |
| Loading / empty / refetch contracts | `STATE-*` | 9 | 6 |
| Errors as toasts | `frontend.md` errors | 9 | 7 |
| Bulk partial failure | `BULK-*` | 8 | 7 |
| Unwired capability is not dead code | `DEAD-CAPABILITY` | 7 | 2 |
| YAGNI and debloat-on-touch | `authoring.md` preamble | 7 | 5 |
| No inline CSS | `frontend.md` styling | 6 | 5 |
| Test value per PR | `testing.md` test value | 5 | 5 |
| Covering index per query path | `INDEX-COVERING` | 3 | 3 |
| Every manual bug becomes a test | `testing.md` bug→test | 3 | not validated; reported 5 |
| Branded types | `authoring.md` type safety | 2 | 2 |
| No pre-production backfill | `authoring.md` database | 1–2 | 2 |
| Never re-pin an assertion | `testing.md` contract | **0** | 0 |
| No rate limiting in application code | `authoring.md` | **0** | 0 |
| Fleet orchestration, all rules | `orchestration.md` | **0** | 0 |

The two unvalidated spreads above exceed their finding counts, which is impossible under the stated per-comment counting method. They are preserved as historical reports, excluded from quantitative ranking, and need a source-level recount. The original extraction and classification script is not included in this checkout.

**The review loop is the strongest signal in the corpus and doesn't fit the table.** 382 author fold-replies across **179 distinct PRs** — 54% of every PR in the repo — plus 18 raises about the loop itself.

Three secondary corroborations worth citing:

- The dead-code check is named in **89 comments across 51 PRs** — the most consistently-run single gate step, which motivated the original always-loaded `DEAD-EXPORT` rule. Current guidance also accounts for framework discovery and required capabilities.
- Three PRs ran formal design-drift defect tables (`D1…D10`) against the design bundle. Design fidelity earned its status as a hard gate.
- The corpus cites the origin project's own house-rule files 39 times across 15 distinct rules — an independent map of which rules were actually codified, and it agrees with the regex counts.

## What the data disproved

This table records the original audit and its response. These rules were retained as targets, with mechanisms rewritten to make them checkable. Retention was an engineering decision; observed compliance does not establish that a rule is necessary or effective. Later revisions must also consider deliberate product changes and deployment context.

| Claim as written | What the data shows | What changed |
|---|---|---|
| PR body carries the literal line `E2E full suite: N/N pass` | **0 of 319** merged PR bodies contain it. `Browser smoke` reaches 40/319 (12.5%) and only appears in the project's final week. A generic test-plan section reaches 272/319 (85.3%). | The literal-string mandate is gone. Full-suite-before-raising is now an explicit **aspirational target scoped to functional-code PRs**, reported with real numbers; design-pass, docs, and chore PRs are out of scope. |
| Zero test skips; the audit grep returns zero before push | The project's own gate lines repeatedly advertise `1331/1331 passing (10 skipped, 1 suite skipped)`, and one harness was built to auto-skip with a warning. | Zero is still the target. `TEST-SKIP` adds the mechanism that makes it enforceable: skips are a **declared baseline that may only go down**, reported on every gate line, and claiming zero when it isn't is worse than the skips. |
| Review→fold→re-review terminates in ≤2–3 folds | 30.4% of PRs needed 3+ rounds, 10% needed more than 10, one accumulated 26 review events. Round-numbering markers show median 2, max 9. | `REVIEW-ROUNDS` keeps two as the expectation and replaces the round-count escalation trigger with a **diagnosis**: escalate when a class recurs across rounds, when a fold regresses a fixed defect, or when new findings still arrive in untouched files. |
| URL discipline is deliberately *not* enforced by a custom static walker | Repo A built three (`check-fe-be-contract.ts`, a realm-scoped-path checker, a bundle-size walker) and ran them as gates. One then **blocked the correct architectural fix**: it resolved only string-literal route arguments, so swapping to the typed constant this skill mandates registered as a violation. | `URL-ENFORCE` keeps layered enforcement as the default and adds the conditions a custom checker must meet — it must resolve the typed constant, ship its own tests, report file-and-fix, and be owned. When it blocks a correct change, the checker is the defect. |
| Backend and frontend PRs alternate | FE-only 90 vs BE-only 36 — a 2.5:1 ratio, not alternation. 25% of PRs in the review era carried no marker at all. | The alternation rule is unchanged, and the data supports its stronger half outright: **"never one PR touching both sides" held with 1 violation in 319.** |
| ≤20 files per feature PR | 87.8% comply. 39 breaches, p90 = 22, max 353 files. | The budget stands, and the *direction* is genuinely supported: compliance rose 82.1% → 90.6% → 90.7% across the project's thirds while p90 fell 31 → 20 and the median fell 8 → 5. |
| Every PR gets a reviewer, no exemption | 14.2% of review-era PRs merged with **zero** reviews, and 70% carried no review thread at all. | The rule is unchanged; `review.md` now states plainly that an automated reviewer is a real reviewer for coverage purposes but is **not** a human approval, and a PR that only had automated review says so when surfaced for merge. |

## Recurring defects the skill did not previously cover

These seven were added during the original corpus audit. Rule numbering and "new" labels in this historical table refer to that release.

| Defect class | Evidence | Where it landed |
|---|---|---|
| A query, write, or storage path dropping the scope key | 12 raises / 5 PRs, **including one re-introduced on the same file after being fixed**, and a fold that had to add a pre-save invariant hook across 15 models. Plus 29 raises / 20 PRs on scope resolution and path ownership. Highest-severity class in the corpus. | `tenancy.md` (new), and non-negotiable #1 |
| An unwired capability deleted as dead code | 7 raises / 2 PRs, all rejecting deletions — "it's like deleting a capability", "this should be wired in for completion and tested". | `DEAD-CAPABILITY`, and non-negotiable #6, which previously said the opposite |
| Accessibility | 17 raises / 14 PRs, 14 of them automated — a top-5 class against a single passing ARIA mention in the old version. Plus 6 raises / 3 PRs on focus-visible and reduced motion. | `accessibility.md` (new) |
| Loading / empty / refetching confusion | 9 raises / 6 PRs, including a 220ms artificial delay in front of a synchronous computation. | `STATE-*` |
| Cross-PR contract drift and dead cache keys | 10 raises / 10 PRs on dual-mount cutovers, plus the canonical shape: an invalidation on one key string while the subscriber used another. | `MIGRATE-*` |
| Naming and test-id taxonomy drift | 18 raises / 15 PRs. Test ids are load-bearing for e2e rules the skill already mandated, so this was a coherence gap. | `NAME-*`, `TESTID-*` |
| Silent partial failure in bulk operations | ~8 raises / 7 PRs. Sequential awaits over N ids where item 3 fails after 1 and 2 committed, then a rollback restores the full pre-mutation snapshot. | `BULK-*` |

## Eight rules from a single production session

Not from the two-repo corpus above — these eight came from real defects found in one later production review session, reported here as instance counts rather than regex-counted raises across a corpus.

| Defect class | Evidence | Where it landed |
|---|---|---|
| Authorization helper silently exempting a caller class | 1 instance — `assertPermissionByActor`'s `SERVICE_ACCOUNT` branch never asserted, and every `Actor`-typed authorization overload routed through it, silently unauthorizing three endpoints. | `SCOPE-NOOP` |
| Client-supplied filter standing in for the authorization boundary | 1 instance — a lookup endpoint took `?patientId=` chosen by the caller; inverted so the boundary derives from the authenticated actor. | `SCOPE-NARROW` |
| A usage search licensing deletion of a domain field | 1 instance — a message `type` field dropped after a grep found no readers; its absence made an empty text message indistinguishable from an image with no caption, and a triaging consumer silently treated images as empty. | `DEAD-CAPABILITY` (extended) |
| Foreground gate abandoned mid-run and reported as complete | 2 instances — a backgrounded Maven suite stopped with no live child, reported as still running; a Testcontainers suite that could not start for lack of a Docker daemon, correctly reported as not-run rather than passing. | `orchestration.md` gates (new) |
| A restored shared field retyped instead of restored as-was | 1 instance — a field deleted from a domain model during a client migration came back after review typed differently from the original, forcing an unrelated legacy mapper to invent a UTC assumption converting a display-formatted date; restoring the original type removed the need for any conversion. | `TOUCH-BLAST` |
| A disclosed judgment call accepted instead of interrogated | 2 instances, both caught only on a second pass — "verified zero consumers via grep" justified the same field deletion above, sound on the usage question and silent on the semantic one; the UTC assumption above was disclosed as a tradeoff in the PR body, which answered "is this honest" and left "why is this in the diff" unasked. | `REVIEW-DISCLOSED` |

`SCOPE-OPAQUE` and `REUSE-CONTRACT` are included in this version on the same review's judgment call rather than a distinct logged instance; keep that in mind when weighing them against the rest of this table.

## Six rules from watching an agent fleet

From Repo C, during a multi-phase frontend migration run by a fleet of coding agents. Instance counts, not regex-counted raises. Small numbers — but each one is a case where **every gate was green and the work was wrong**, which is the only reason these rules exist at all: they are the checks that would have caught what the gates structurally could not.

| Defect class | Evidence | Where it landed |
|---|---|---|
| A capability deleted end to end, hidden behind a green suite | 1 instance — 538/538 passing while a clinical-scoring capability was gone: the payload field hardcoded to a constant, the form control removed, the attribute write-back dropped, and the guard that enforced the rule left as unreachable dead code. Green because the agent **deleted the failing test and left a comment asserting the removal was intentional.** Only a base-vs-branch behavioural diff surfaced it. | `REGRESS-DIFF`, and non-negotiable #14 |
| A test harness masking a total boot failure | 1 instance — 648/648 unit tests passing while the application threw on every route in the browser. A component gained a context-dependent hook; its own test wrapped it in a provider that the real composition never supplied. Caught only by the CI browser suite, as 9 failures across 5 specs all reporting the same uncaught error. | `HARNESS-MASK` |
| Markup changed, browser specs not | 1 instance — a control deliberately replaced per the design, with briefs saying "preserve every test id" (impossible for a replaced control) and no agent tasked with the spec pass. Unit tests 630/630 locally; CI red on selectors that could no longer exist. | `SPEC-PASS`, `ID-INVENTORY` |
| One agent given all the structural work | 1 instance — a single phase-wide agent ran 2+ hours and finished with 18 test failures, having changed every component before running the suite once. Failures arrived entangled, at the point of least remaining context. | `orchestration.md` decomposition, incremental gates, checkpoint |
| Isolation rule read backwards | 1 instance — "worktree isolation is the default" was read as needing justification, so a round of independent agents ran serially in one checkout for no reason. | `orchestration.md` isolation |
| Briefs that bury their own invariants | 1 instance — briefs grew to ~120 lines of prose restating every non-negotiable verbatim; the first PR under one ballooned in scope and had to be closed and restarted. | the contract card in `SKILL.md` |

`CLAIM-EVIDENCE` and `TEST-NODELETE` have **no independent instance** behind them. They are positions taken in response to the two failures above — the first generalises "a gate claimed without a number is not evidence" to every compliance claim, the second closes the subsumption carve-out that green-by-deletion hid behind. Weigh them accordingly.

The honest caveat on this whole table: n=1 on every row, one repo, one migration, one operator. What makes them worth publishing is not their frequency but their **detectability** — in all six the ordinary signals said the work was fine, so no amount of running the existing gates harder would have surfaced them.

## What a live A/B showed

One paired run, with the plugin and without, on the same prompt: review two new functions in a Python and SQLAlchemy service — a stack deliberately unlike the origin codebase — where both functions dropped the scope key. **One run per arm, one file, one stack. This is a smoke test, not a benchmark.**

What the skill added over the baseline:

- Named the covering index the fixed query would need, leading with the scope key and carrying the sort key. The baseline never mentioned indexing.
- Demanded the negative tests — one asserting a list excludes another account's rows, one asserting a foreign id is refused. The baseline didn't mention tests at all.
- Folded everything into one punch list for the same PR, explicitly rather than leaving items to trail.
- Treated the raw status string as a rule violation with its casing-drift consequence, rather than a minor note.
- Used the `blocker` / `should-fix` / `nit` vocabulary, and the prose review shape with no verdict header.
- Bound the scope key to this repo's `account_id` and derived the toolchain from `pyproject.toml`, citing `pytest` and `mypy`. No trace of the origin stack.

**What the baseline did better, and this matters:** it went deeper on framework-specific correctness — it caught an `expire_on_commit` trap that would raise in the caller after commit, and named the concrete failure modes for a shared module-level session. The skill run flagged the shared-session concern but missed the commit-expiry bug, and shipped fewer code snippets.

On this one small diff, both arms found correctness bugs and the baseline found one the skill arm missed. The skill added coverage of indices, negative tests, seed data, folding discipline, and severity language. Whether those gains generalize requires repeated, held-out tasks; this run supports no reliability or effectiveness claim.

## Caveats

State these alongside any number from this file, or the numbers mislead.

1. **"Reviewed" means automatically reviewed.** All 84 approvals and all 11 change-requests in Repo A came from an automated reviewer. The human identity issued **zero** approvals — only comments. So "85.8% of PRs reviewed" is a statement about automation, not about human sign-off.

2. **No before/after comparison is possible.** 318 of Repo A's 319 merged PRs landed inside a single 25-day window. The repo's highest-output weeks came *afterward*, under a local-merge flow that produces no GitHub review artefact — so PR-comment data systematically **under-measures** later review activity. Rework-vocabulary rates per commit also rose across the project's life rather than falling. Nothing here should be read as "this discipline reduced defects over time"; the corpus cannot support that claim in either direction.

3. **Repo B is not a control.** 98 of its 101 PRs are dependabot, it has four-plus human committers against Repo A's effectively one, and it is polyglot rather than single-stack. Its two rework indicators point in opposite directions — 42% more `fix`-prefixed commits per unit of output, but 3× fewer explicitly rework-worded ones. It is a contrast, not a counterfactual.

4. **Counting is regex-plus-reading, not adjudication.** Classification is a judgment about what a comment was *about*. The original raw snapshot and classifier are not distributed here, so the aggregates cannot be independently reconstructed from this checkout. Treat the supported tiers as ordinal, not the integers as exact.

5. **Fleet orchestration still has no *corpus* evidence.** Orchestrator behaviour doesn't surface in PR comments, so nothing in `orchestration.md` or `verification.md` is regex-counted. What changed in this version is that several of those rules now name a specific failure they were written after, in the Repo C table above — n=1 each, from one operator. That is better than assertion and much weaker than the frequency table. Adapt freely.

6. **Repo C's numbers are self-reported, not reconstructed.** The counts in its table (538/538, 648, 18 failures) were recorded during sessions rather than recovered from an API afterwards. The commands below do not reproduce them.

## Twenty rule families from a reported 9-week audit

The commit that added these rule families reported evidence from two further private codebases, referred to here as Repo D (an asynchronous document-matching service) and Repo E (an API gateway, dependency management), and from this skill repository: 122 commit lines (105 unique subjects), 4 PRs with teammate raises (Repo D: 6 and 9 raises; Repo E: 4 and 1), and 37 rework commits. Those aggregate classifications were not independently reproduced in the later local-history review; they remain reported evidence, rather than verified incident totals.

**Scope and counting:** Aug 12–Oct 14 is 9 weeks, not the author's entire history. Commit counts measure slicing; subjects are not reliable deduplication keys. A claim/fence implementation, a test class, a review raise, and a corrective commit are different units. Same-branch rework is self-detected, not a review finding. Several commits can belong to one failure sequence. The ranks below are the original priorities, not a comparable frequency ranking.

| Priority | Rule ID | Rule | Reported signal | Repos | Severity | Reference |
|---|---|---|---|---|---|---|
| 1 | LOG-FAILURE / LOG-LENGTH | Keep sensitive content out of telemetry and error responses | 7 | D + E | blocker on data-bearing paths | `observability.md` |
| 2 | COMMIT-TRUTH | Commit subject describes diff; no same subject over different diffs | 6 | D + E | should-fix | `workflow.md` |
| 3 | JOB-LEASE | Exclusive job execution via database lease | 5 | D | blocker | `async-jobs.md` |
| 4 | MIGRATE-ROLLING / MIGRATE-IMMUTABLE | Safe schema migrations for rolling deploys | 5 | D | blocker | `workflow.md` |
| 5 | REPRO-FIRST | Establish the failing path and state reproduction limits before changing error behavior | 4 | D + E | should-fix | `review.md` |
| 6 | LOG-SENTINEL | Content-bearing failure sinks get meaningful leak-sentinel coverage | 11 test classes | D | should-fix | `observability.md` |
| 7 | DEP-PIN-SUPPRESS | Overrides/suppressions carry rationale, applicable advisory, and removal condition | 4 | E | should-fix | `dependencies.md` |
| 8 | DEP-BOOT | Real app boots after upgrade; diff transitive tree | 3 | E | blocker | `dependencies.md` |
| 9 | LOCK-MINIMAL | Choose the smallest correct serialization mechanism for the actual datastore/isolation level | 3 | D | should-fix | `authoring.md` Database |
| 10 | CONFIG-FAIL-CLOSED | Secrets get no production default; invalid config fails at startup | 4 | D | should-fix | `authoring.md` |
| 11 | TEST-PIN | Characterization tests must fail when behaviour changes | 3 | D | should-fix | `testing.md` |
| 12 | TEST-CONCURRENCY | Every exclusivity claim tested against real database | 5 test classes | D | should-fix | `testing.md` + `async-jobs.md` |
| 13 | JOB-FENCE | Claim with token; finalize filters on scope + id + token | 4 mechanisms | D | blocker | `async-jobs.md` |
| 14 | JOB-RETIRE | Mark obsolete, not deleted; retire after complete crawl only | 3 | D | should-fix | `async-jobs.md` |
| 15 | JOB-GATE-ORDER / TEST-GATE | Gates checked cheapest first; one test per gate | 7 tests | D | should-fix | `async-jobs.md` |
| 16 | NAME-FULL | Clear names in the repository's vocabulary; avoid ambiguous abbreviations | 3 | D | nit / should-fix | `authoring.md` NAME-* |
| 17 | LLM-FAILSAFE | Model output checked against request and authorized domain constraints | 3 | D | impact-dependent | `llm-calls.md` |
| 18 | LLM-CORRELATE / LOG-FIELDS | Privacy-reviewed correlation propagated through stage and attempt | 3 | D | should-fix | `llm-calls.md` + `observability.md` |
| 19 | LOG-LENGTH / LLM-PROMPT | Minimize model inputs and log untrusted content safely | 2 | D | should-fix | `observability.md` / `llm-calls.md` |
| 20 | BRAND-SCOPE | Brand only where mix-up is possible; avoid ceremony | 2 | D | nit | `authoring.md` Type safety |

**Data that disproved existing rules:**

| Earlier claim | What the data shows | Action |
|---|---|---|
| CONFIG-DAY-ONE: "every config service carries a hardcoded default" | A reported Repo D commit removes production defaults; missing values fail startup | `CONFIG-FAIL-CLOSED` separates optional tuning defaults from secrets and required production configuration |
| Branded types mandatory | A reported Repo D review reversal after over-application through CLAUDE.md | `BRAND-SCOPE` requires a concrete mix-up risk; use the language's native domain types where appropriate |
| TOUCH-BLAST | The audit reported violations by its own author | A written rule is not enforcement; check behavior against the base and distinguish cleanup from unrelated changes |

**Issues reported at that audit's snapshot, not reverified as current defects:**
- Three REST controller error paths in Repo D return raw exception messages in HTTP error bodies
- One outbound client in Repo D puts the upstream message into a wrapping exception
- Repo D's structured logger still has `warn`/`error(…, Throwable)` overloads

## Local authored-history review, October 14, 2026

The enhancement after the four-guide commit inspected the available authored history across local checkouts, rather than treating the 9-week subset as the entire history. This is a reachability inventory and a set of inspected examples, not a new defect-frequency study.

| Source | Verified scope | Limits |
|---|---|---|
| This skill repository | Non-shallow; 7 commits reachable from the reviewed HEAD (the commit that added the four guides), 13 unique objects across local branches, tags, and remote-tracking refs | Pre-squash branch commits and the resulting squash commits describe overlapping work; 13 objects are not 13 independent changes |
| Other local checkouts in the author's workspace | 41 repository/worktree directories, 40 common Git directories, 31 repository basenames; 18 basenames had commits matching the author's known identities | Repeated checkouts and worktrees are present; these are discovery counts, not counts of independent applications |
| Authored commits in those other checkouts | 953 globally distinct hashes, July 9–October 14; 913 non-merge; 907 after excluding 6 non-merge stash-like snapshots; 539 nonempty stable patch IDs; 486 distinct exact subjects | Excludes this skill repository. Hashes, patch IDs, and subjects count different things; none counts defects or independent incidents |

The inventory used locally reachable `--all` refs, recorded commit identities and parent hashes, and deduplicated hashes across checkouts. It did not fetch remotes or inspect deleted branches, reflogs, or unavailable repositories. An empty patch ID is excluded from the patch count; matching patch IDs help identify repeated patches, not semantic equivalence. Attribution depends on recorded author identities. This is the available local history, not a claim to have inspected the author's entire remote history.

Selected verified examples:

| Repository and commits | What the inspected diff establishes | Guidance it informs |
|---|---|---|
| Repo F (clinical reporting), two commits | A two-commit sequence adds report-start filtering and deterministic measurement selection, then aligns calculated BMI with the height printed in the report | `APP-DATA`: define temporal selection and cross-field consistency; this pair is one sequence, not two independent incidents |
| Repo G (message triage), one commit | Processing follows the event's message ID instead of asking for the latest message, which can refer to a newer event | `IO-IDEMPOTENT`: preserve event identity through asynchronous processing |
| Repo G (message triage), one commit | A frontend feature gate protects use of a new backend endpoint that was merged but not yet deployed | `DELIVERY-READY`: verify deployed compatibility and release order, separately from merge order |
| Repo H (eligibility frontend), one commit | Cypress expectations change after an intentional initial-selection change from one medication to another | Counterexample to immutable assertions: preserve coverage while updating tests to an explicitly changed acceptance contract |
| Repo H (eligibility frontend), one commit | Draft branch state is retained separately from saved active-branch values, with tests for excluding hidden notes from save | `STATE-DRAFT` and `INPUT-BOUNDARY`: check the persisted result, including omitted and inactive fields |
| Repo H (eligibility frontend), two commits | Medication rendering gains an explicit flag guard; a later AI-preview change prevents save until the preview is resolved | `AUTH-BOUNDARY` distinguishes flags from permission; `STATE-ASYNC` separates suggested values from committed user intent |
| Repo D, one commit | Semantic wrappers are removed from pass-through call chains while retained at a boundary with meaningful validation | `BRAND-SCOPE`: use domain types where they prevent a concrete error, without mandatory wrapper propagation |

These examples support specific checks, not the effectiveness of the complete skill. The new application-design, security, integrations, and delivery guides also contain supplemental engineering judgment. Broader requirements for threat modeling, time budgets, idempotency, readiness, and recovery are useful production practices, but this audit does not supply an independent observed defect behind every clause. Keep that distinction when adapting or evaluating them.

The skill's own history suggests a maintenance control: `6b6b7de` added production-session rules, `69f64b8` added checkable verification and consolidated authorities, and the four-guide commit added async, observability, LLM and dependency guides while leaving several advertised reversals and cross-reference rules only in this evidence file. Evidence that changes a rule must update its executable guidance, trigger, and review path together. A provenance table alone does not change agent behavior.

## Reproducing this

For the original PR corpora, these read-only API calls acquire source records. They do not reproduce the historical snapshot, the regex classification, session reports, or commit-history aggregates by themselves:

```bash
gh api --paginate 'repos/<owner>/<repo>/pulls/comments?per_page=100'
gh api --paginate 'repos/<owner>/<repo>/issues/comments?per_page=100'
gh pr list --repo <owner>/<repo> --state merged --limit 400 \
  --json number,title,changedFiles,additions,deletions,mergedAt,body,reviews
```

For commit-history work, the bundled `skills/craft/scripts/history_inventory.py` accepts explicit `--root` and `--author` arguments; `--manifest --patch-ids` adds ref/hash coverage and patch-equivalence measures without raw commit bodies. Discovery stops at a repository; provide nested repositories as additional roots. Stash-like subject classification is heuristic. Retain those limits along with identity matching, ref/HEAD snapshot, and exclusions. Inspect actual diffs for each cited case; repeated subjects and corrective wording are leads, not findings. Example read-only checks within a checkout:

```bash
git rev-parse --is-shallow-repository
git for-each-ref --format='%(refname) %(objectname)'
git log --all --format='%H %P %aI %an <%ae> %s'
git show --format=fuller <commit>
git show --no-ext-diff --format= --binary <commit> | git patch-id --stable
```

To test whether the skill helps, use held-out base/fix cases across stacks and repeat both skill and baseline runs. Record correct findings, missed defects, false positives, regressions introduced while fixing, and cost. Keep deliberate product changes as counterexamples. Commit counts, greener suites, or fewer review rounds alone cannot establish improvement.
