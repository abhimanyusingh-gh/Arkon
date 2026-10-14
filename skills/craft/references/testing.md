# Testing

Choose checks that can detect a real failure of the changed contract. Preserve meaningful regression and safety coverage; avoid tests that merely mirror implementation details or create ceremony for reversible copy/style changes.

## Seed data

New behavior needs representative synthetic test data. Extend existing factories/fixtures or the demo seeder when that behavior is meant to appear in the demo dataset; not every type or service needs a global seed row.

Useful cases include:

- New status value → one record at that status.
- New signal → one entity carrying it, open.
- New service → 1–3 representative records covering its main paths.
- New accumulator or running total → one row at the threshold and one above, so boundary math is visible.
- New relationship → both sides seeded, so a test can exercise the join rather than assuming a row exists.

Reusable seeders identify records by a stable, scope-aware key and have a documented repeat-run policy. Do not make a test depend on incidental fixture ordering or unrelated rows.

**Seed the entities the test contract requires.** Create prerequisites explicitly. If the product contract is unchanged and a required fixture is absent, repair the fixture rather than weakening the assertion. An obsolete fixture may change with an intentional contract change (`TEST-PIN`).

**SEED-MODE — destructive setup belongs only in isolated disposable test data.**

- Drop/reseed or snapshot restore only a datastore provisioned for that suite and verified disposable. A label such as "dev" or "staging" is not proof. Guard against a mistaken connection string before destructive setup; never reset shared, staging or production data to run tests.
- Shared/demo bootstrap is separate from test reset. Where authorized, add missing seed-managed records without deleting user-created rows or overwriting user edits. Use scope-aware natural keys and report what was inserted/skipped; deliberate reference-data updates need their own migration policy.
- A repeated production bootstrap must not overwrite an existing administrator account or reset its credentials. Demo-only data stays disabled where real data lives; the presence of credentials does not authorize running a seeder.

When changing seed modes, verify additive setup preserves a user-mutated row, inserts a missing row, and leaves unrelated rows untouched. Verify the destructive mode refuses a non-disposable target.

Parallel tests need separate databases/schemas/scopes or another proven isolation mechanism; restoring one worker's global snapshot must not erase another worker's state.

## Invariant tests over happy-path

For important calculators, projectors and derived displays, test the domain invariant as well as named examples. State assumptions and units first; an equation is only an invariant if the domain guarantees it.

- **Backend:** cover boundaries, rounding, units, null/zero distinctions and relevant modes. Use hand-calculated contract examples, independently derived/reference results, or properties such as conservation/monotonicity where valid. Copying the production formula into the test can reproduce the same bug twice.
- **Frontend:** check that displayed inputs and derived results refer to the same selected source and remain consistent across meaningful fixtures. Do not use the rendered total as the oracle for the rest of the screen.
- **E2E:** choose representative user scenarios and high-risk interactions. For broad generated/property-based combinations at a cheaper layer, see `PBT-PROPERTY` below; do not require the full Cartesian product in a browser.

The failure this prevents: every layer has complete-*looking* tests for its own scope, while no assertion says "for any rendered row, the body value equals the footer value equals the computed difference." That's how an internally-inconsistent display ships — a label reading 0% next to a non-zero amount.

**Exhaustiveness is part of an exhaustive claim.** A check of 4 of 15 dependent tables cannot prove the whole datastore invariant. Derive the relevant population from metadata where reliable, and account for deliberate exclusions; metadata traversal alone does not establish semantic relationships.

Preserve the important invariant through refactors, even when its test moves to a different layer.

## PBT-PROPERTY — test properties and boundaries with generated inputs

Property-based testing uses randomly generated input to find counterexamples to an invariant. Use it for parsers and serializers, calculators and derived values, validators, state machines and transition tables, deduplication, sort and merge, idempotent operations, and round-trip conversions (encode/decode).

**When to use:** build generators from the domain with boundary values, null, zero, unicode and large sizes; avoid filter-heavy generators. Test properties including: round trip (encode/decode returns original), idempotence (apply twice = apply once), invariant preserved (preconditions imply postconditions), oracle/model comparison, metamorphic relations, and "total function never throws".

**Warning:** do not restate the production formula as the oracle (replicates the same bug twice, like `CLAIM-EVIDENCE` in verification.md for invariants). Use hand-calculated examples or a reference implementation.

**PBT-REPRO — pin discovered counterexamples and bound example budgets.**

- Log the seed on failure and persist failing examples in version control.
- Each discovered counterexample becomes an explicit pinned example test.
- Set a per-test example budget (e.g., 1000 cases) so CI time is bounded.
- Decide whether CI runs deterministic (fixed seed) or randomized explicitly, and state the tradeoff.
- Report the generator, example count and seed in the gate line.

**Tool examples:** Hypothesis (Python), fast-check (JavaScript), jqwik (Java), proptest (Rust).

## TEST-CONCURRENCY — prove the datastore guarantee being claimed

Use the real datastore engine/version and relevant isolation/index configuration for atomicity, exclusivity, scope and locking claims. A mocked repository or an in-memory substitute cannot prove production lock semantics.

- Coordinate genuinely overlapping operations on separate connections/transactions with barriers or explicit latches. Check that the harness has enough connections to exercise contention instead of serializing the test accidentally.
- Assert durable outcomes: one winner for a unique create/claim, no lost update, stale version/token rejected, and the declared conflict/retry outcome for losers. Include an initially missing key when the algorithm relies on locking a lookup.
- Exercise the relevant rollback, crash/reclaim, expiry and retry boundary. Bound retries and test waits; arbitrary sleeps are weak evidence of overlap. Use controllable expiry/clock setup where supported.
- Inspect results after commit and repeat races when useful. A stress run can reveal a race; it does not replace the constraint/transaction mechanism that prevents it. See `LOCK-MINIMAL` in `authoring.md` and `TEST-LEASE` in `async-jobs.md`.

## Test-id contract

Selectors connect product behavior to its tests. Prefer accessible role/name/label queries when they identify the intended user control; they also check part of the accessibility contract. Stable test ids are useful for ambiguous or non-semantic elements.

**TESTID-SCHEME — follow the existing scheme where ids are needed.** A scheme such as `<surface>-<element>-<variant>` can help. Avoid personal content, unstable indices and visual implementation details in ids. Reuse a builder when it serves actual consumers; do not add one merely to type every selector.

**TESTID-STABLE — target the intended behavior.** Prefer semantic queries or stable ids over incidental classes/DOM position. Text queries are appropriate when text or an accessible name is the requirement. For changed markup, inspect selector consumers and preserve or deliberately update their behavioral coverage (`ID-INVENTORY` in `verification.md`).

**TESTID-COVER — important behavior is queryable.** Cover the control/result using an accessible selector or stable id as appropriate. Do not attach test ids to every static design element by default.

## E2E rules

For browser behavior tests:

1. Use behavior-focused names and follow the repository's test conventions.
2. **Config lives in one shared place** — timeouts, viewport, retries, network policy, fixture paths, credentials, env gates in the config file and shared helpers. Specs consume, never redefine. A per-test timeout override is allowed only when one test legitimately needs longer, with justification.
3. **Never "account for network issues."** No catch-and-continue around navigation, fetch, or response waits. Fix the upstream flake instead of papering over it.
4. **Real user actions for everything under test.** Click the control. Don't drive the app by evaluating fetch in the page, don't call the API client. Direct API calls are for the *arrange* phase only (reset a scope, seed an entity).
5. Assertions must fail the suite. Soft assertions are acceptable only when their accumulated failures remain fatal; never swallow a failed action or assertion and report success.
6. Use bounded action/navigation deadlines appropriate to the product and CI, with condition-based waits. Avoid arbitrary sleeps and extending timeouts to hide a failing dependency.
7. Assert the visible result of state-changing actions. Also inspect durable backend state when persistence, optimistic updates, eventual consistency or a critical running total is part of the contract; do not require an extra backend poll after every purely local UI action.
8. Expected values come from the requirement and independent examples, not the current production result/formula. Exact assertions help for deterministic amounts/statuses; visibility is sufficient when presence is the behavior under test.
9. **Sequential journeys are one continuous-state test**, not N isolated steps with mocked starting state — that's what catches state-bleed. Independent table-driven arithmetic cases legitimately stay separate.
10. **Cover side-effects of user-driven config changes.** For any field the user can edit, assert the downstream derived field actually re-derives. A critical gap, not a nit.
11. Cleanup attempts must not turn a failed assertion into a pass or hide the original failure. Preserve primary and cleanup failure evidence; do not silently catch either.
12. Verify important displayed arithmetic against independently known expected amounts, including rounding/formatting boundaries where they matter. Sharing a formatting helper may be appropriate when formatting is not under test; it cannot prove that same helper formats correctly.
13. Cover the relevant empty / one / many / loading / error states and filter/reset effects. Assert required content and interactions, rather than duplicating every DOM node across every scenario.
14. Keep mutable tests independent and safe to retry through disposable-data fixtures, scoped cleanup, transactions or snapshots as supported. A global reset is allowed only for a verified isolated disposable database and must not race other workers (`SEED-MODE`).
15. **Cover the feature's primary path, not only its edges.** A suite that exercises every filter but never the document upload the product exists to perform is not covering the product.

**TEST-SKIP — skipped coverage is visible missing evidence.** Report counts and reasons, including environment/credential limitations. Do not conditionally pass because a required fixture is absent or quarantine a regression just to get green. A legitimate temporary exclusion follows repository policy with a reason, owner and review condition; it remains a limitation in the result.

An environment-gated suite names its missing capability and is counted as skipped/not-run, never passed. Do not request or expose production credentials merely to avoid that limitation.

## E2E execution gates

Run added/modified tests and the applicable repository gates before claiming verification. Focused runs help the inner loop; final coverage follows the repo's required commands and the affected boundaries. Observe the command through completion; report not-run checks and environment failures honestly.

For changes spanning composition, UI state, contracts or shared infrastructure, run the relevant full end-to-end gate against a stack built from the tested revision. A changed-file run cannot establish unaffected consumers still work. Use the production/root composition rather than a test-only provider tree (`HARNESS-MASK` in `verification.md`).

Record revision/artifact, command, completion/exit status, pass/fail/skip counts and relevant configuration. If later edits affect the result, rerun the applicable checks. Do not treat a stale image or previous branch's green suite as current evidence.

Docs, reversible copy changes and narrow presentation changes need checks proportional to their impact, including visual review where appropriate; they do not automatically require new tests or the full browser suite. Investigate failing checks against a clean baseline when needed and report known unrelated failures rather than hiding them or widening scope without reason.

Choose a useful layer for changed behavior: a new user journey or redirect often needs a browser check; a domain calculation needs independent unit/property examples; a persistence guarantee needs datastore integration. Update affected existing specs with the implementation. Do not postpone essential regression coverage to an unspecified follow-up.

Organize specs by behavior/surface using the repository's existing fixtures and authentication setup. Exercise the real login journey in its own coverage; other suites may use supported session setup to focus on their behavior without repeating authentication on every test.

## Test value per PR

When writing a test, ask:
1. Does an existing test cover this behaviour? → extend it (another case in the same suite, another table row).
2. Am I testing real behaviour, or a mock? A test that "the wrapper calls fetch with these args" tests the mock.
3. Would this ever fail for a real bug? If it only fails when someone edits the test setup, delete it.
4. Is the same fact already statically enforced? Avoid a tautological runtime test, while retaining boundary validation, migration and runtime coverage that static types cannot provide.
5. Am I duplicating coverage across layers? Pick the highest-value layer (usually integration against a real datastore harness) unless the lower layers cover unique edge cases.

An assertion that repeats an implementation literal without an independent requirement usually adds little. A fixed protocol or permission allowlist can be a meaningful external contract; verify it at the boundary where incorrect values would matter.

Put cases where they form a coherent suite. A new test file is a normal organization choice, not something requiring a separate justification. Reviewers look for valuable coverage rather than rewarding case counts.

Test consolidation or deliberate capability retirement may reduce test counts; account for the protected/retired contract and replacement coverage under `TEST-NODELETE` (`verification.md`). A count change alone proves neither improvement nor regression.

For unchanged behavior, preserve critical business, security, historical-regression and real-datastore guarantees when reorganizing tests. Replacing their location is legitimate; dropping their protection to reach green is not.

## Read the tests before rewriting the code

Before changing a component, read its test file and map every assertion to the element it targets. Then implement. Doing it in this order surfaces compatibility breaks before the code is written; doing it after turns them into a fix loop, and the loop is where tests get quietly deleted to make it stop.

A test that needs a provider the application does not supply proves nothing about the application — `HARNESS-MASK` in `verification.md`.

## Regression tests for discovered bugs

For a meaningful behavior, safety or recurring defect, add a regression that reproduces the failure and passes after the fix. Demonstrate red-before/green-after when feasible; otherwise state the reproduction limit and provide another useful check.

- Assert the externally meaningful wrong value or transition with an independent expected result.
- For a reversible typo or low-impact visual correction, inspection/smoke can be sufficient; do not add a brittle literal test solely to satisfy a rule.
- A validator shipped without a case exercising the format it validates is the same gap one step earlier.
- A shrunk counterexample from property-based testing becomes a pinned example test (`PBT-REPRO`).

Manual smoke and automated regression answer different questions. Preserve useful automated protection for repeatable failures; continue visual, composition and exploratory checks where automation does not establish the product behavior.

## TEST-PIN — preserve intent when assertions change

Tests are evidence of the product contract, not an immutable product specification. When behavior is unchanged, fix a regression in the product, fixture or configuration; never replace an expected value with the observed broken value just to pass.

Changing an assertion is legitimate for an intentional requirement/API/design change, a proven incorrect expectation, or a test/harness repair. State the old and new contract, its source, and the callers/scenarios affected. Update implementation, expectations and docs together, preserving safety/regression checks for behavior that still applies. A request for the product change already authorizes its necessary test updates; do not invent another approval step.

If a still-required fixture is missing, add it; if a required nonempty result becomes empty, diagnose it. Weakening `>= 1` to `>= 0`, deleting an assertion, or skipping a case without a contract reason is green-by-weakening (`TEST-NODELETE`).

Review the requirement and evidence behind an expectation change, rather than treating either every assertion edit or every green suite as trustworthy by default.
