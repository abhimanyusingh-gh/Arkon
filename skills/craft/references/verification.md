# Verification — proving a claim rather than making one

Read when verifying completion, reviewing a refactor, or preparing delivery. Apply checks to the affected contracts; verification does not authorize pushing, publishing or deploying.

Ordinary gates can stay green when a capability and its tests disappear together, or when a test-only composition supplies dependencies production lacks. Compare the intended contract, implementation and runtime evidence instead of relying on an author's assurance or a test count alone.

## CLAIM-EVIDENCE — a gate is proven by its output, not described

Record the command, tested revision/artifact and relevant working-tree changes, completion/exit status, pass/fail/skip counts, and actual output supporting the claim. Include environment/profile when it changes behavior. An adjective is not evidence; a count without its tested revision can describe stale work.

- A gate that could not run is reported as **not-run, by name, with the reason**. Never omitted, never folded into a pass. No container runtime and no browser binary are holes in the evidence, not green lights.
- Observe foreground or asynchronous commands through completion. A session id, started process, partial output or timeout is not a passing result. Report a still-running check as pending; preserve useful failure output rather than inventing totals.
- Re-run checks affected by later edits. Identify any results that cover only an earlier revision, and do not present a previous image/branch's green suite as current evidence.
- Verify load-bearing claims against the right source: diff/callers for code structure, actual logs and test output for execution, plans/measurements for performance, deployed contracts for availability. A claim need not be visible in the diff, but it needs accessible evidence or an explicit uncertainty.
- Use the evidence card for substantial handoffs and concise prose for a small change. Missing tools/credentials are limitations to report, not permission to fabricate a result or mutate an external environment.

## REGRESS-DIFF — diff against the base for what was *lost*

A green suite is not evidence that nothing regressed. On a behavior-preserving refactor or capability-removing change, compare with an identified base revision for **absent** behavior as well as additions. Use these signals to investigate, not as automatic findings:

1. **Domain terms that vanished.** For each touched file, read the base version and grep it for the domain vocabulary the feature is built from. A term present at base and absent now is a capability question, not a style question.
2. **Removed tests and explain-away comments.** Inspect deleted test blocks and comments narrating removals. Trace each meaningful removal to replacement coverage or an intentional contract change; a comment alone does not establish either.
3. **A literal where a variable used to be.** A payload field, flag, or argument pinned to a constant that was previously computed is the signature of a capability quietly dropped to make something pass.
4. **Guards with no reachable input.** A guard reading a prop, field, or config nothing sets is dead code, and dead code means the capability behind it is already gone. Trace one live producer for every guard the change touches.

For substantial or risky work, have the reviewer/orchestrator perform this comparison independently rather than accepting only the author's summary. A local fix can use a separate review pass. Preserve useful autonomy: do not create an agent fleet solely to satisfy a ritual.

## TEST-NODELETE — green-by-deletion is a blocker

Deleting, skipping or weakening coverage solely to conceal a regression is a blocker. For an unchanged contract, fix the product, fixture, configuration or demonstrably defective test. Intentional contract changes may update tests under `TEST-PIN` in `testing.md`.

Legitimate subtractive diffs include consolidation/replacement, removing an incorrect or tautological test, and deliberately retiring a capability within the requested product change. Account for the consequence:

- For replacement, name the invariant/behavior and the replacement test or stronger enforcement. Demonstrate that it detects the relevant failure, using a known regression, a reproducible broken case or meaningful fault injection where practical. A behavior-preserving refactor's test may correctly pass on both base and head.
- For capability retirement, identify the intentional requirement change, affected callers/data/docs, and coverage for surviving behavior. Do not call it dead-code cleanup when the product contract still requires it.
- For an incorrect test, show the contract evidence proving its expectation wrong; the current implementation's output alone is insufficient.

Preserve critical business/security invariants, historical-regression protection and real-datastore guarantees for unchanged behavior, even if tests move. Name the load-bearing checks in risky handoffs. A shrinking test count is a review signal, not proof that a capability was lost.

## HARNESS-MASK — a test that supplies context production doesn't

A unit test may legitimately supply a provider. It establishes behavior under that dependency, not that production supplies it. A leaf suite can be green while every real route fails at startup.

- Adding a context-dependent hook to a component means checking **where that component is mounted in the real tree**, not only that its own test passes.
- When changing a dependency on root composition, verify the actual mount/registration path. Add or extend a composed smoke test when useful: retain the real shell, changed component and required provider wiring; mock network I/O below that boundary rather than supplying a missing production provider from the test.
- **Confirm the new test fails against the pre-fix wiring** before trusting it. A test that passes against the broken tree is testing the harness.
- Apply the same check outside UI: actual startup configuration, dependency injection, routes, migrations and worker registration. A mocked repository cannot establish lock semantics (`TEST-CONCURRENCY`), and a development/test profile cannot establish packaged startup (`delivery.md`).

**Diagnostic tell:** a wall of browser-suite failures that are all one uncaught application error — rather than a spread of assertion mismatches — means the app never rendered and the specs were never exercised. Fix the boot before touching a single selector. Reading those failures as selector drift and updating selectors buries the real defect.

## ID-INVENTORY — account for every selector before refactoring

When a markup/interaction change can affect selectors, search the whole relevant suite, including shared helpers, for queries reaching the changed surface: test ids, accessible roles/names, labels and text. Account for affected selectors as:

- **preserved** — unchanged, still resolves;
- **renamed** — updated in the component *and* every consumer in the same PR;
- **removed** — with a stated reason.

No silent loss of behavioral assertions. Read affected tests before rewriting the surface; a small change can keep this inventory in review notes rather than a standalone artifact. Accessible queries are valid selectors, not a reason to add test ids everywhere (`testing.md`).

## SPEC-PASS — a DOM or contract change ships its browser specs

Update affected consumer/browser tests with the implementation when a change alters their selectors or product contract. A markup change that preserves behavior and queries need not change a spec, and a backend-only contract may be best covered by integration/contract tests. Essential coverage cannot silently be deferred because it runs only in CI.

1. Grep the whole suite directory for every selector touching the changed surface — **including shared support and command files**, which are the ones that get missed.
2. For each: still valid → leave it. Control replaced → exercise the preserved behavior through the new control. Contract deliberately changed/retired → update with the reason and surviving coverage under `TEST-PIN`/`TEST-NODELETE`.
3. **Never delete an assertion to make CI green.** That is `TEST-NODELETE` in the browser suite, and it fails the same way.

"Preserve every test id" is an impossible instruction for a control the design deliberately replaces, and a brief that says only that will produce a red suite nobody owns. Say which controls are being replaced and who updates their specs.

**Watch blanket assertions.** A spec asserting that no element of some kind exists breaks when an unrelated control legitimately becomes one. Structural changes break specs that never named the changed component, so the grep is over the suite, not over the specs you expect to be affected.

Before declaring a complex application complete, walk its acceptance matrix through real composition: primary journey, authorization/scope denial, important failure/recovery path, and the production artifact checks relevant to this change. State which integrations remain mocked or unverified; do not infer production readiness from unit totals alone.
