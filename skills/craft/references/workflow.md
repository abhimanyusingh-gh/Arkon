# Workflow — scope, migrations, gates, and delivery

Application design lives in `application-design.md`; runtime rollout and recovery in `delivery.md`; delegation in `orchestration.md`. These defaults organize authorized work, not permission to create issues, post reviews, push, or deploy.

## Work intake and slicing

Use an existing issue or the user's request as the source of scope. Record the outcome, acceptance criteria, dependencies, and deliberate omissions. Create or transition tracker items only when that workflow is authorized; derive actual tracker states rather than inventing them.

Slice complex work by a useful, verifiable behavior with a coherent rollback boundary. Prefer small PRs; about 20 hand-edited files is a prompt to reconsider scope, not a correctness rule. Mechanical sweeps can be larger when their review remains reliable. Do not split a change into broken intermediate revisions just to satisfy a file count.

Separate platform upgrades and unrelated cleanup from feature work. Backend-first additive contracts are useful when components deploy independently; a small coordinated frontend/backend vertical slice is valid when it is tested together and preserves compatibility with deployed versions. Dependency order and live capability matter more than alternating PR labels.

Before parallelizing, inspect file ownership and dependencies. Do not dispatch work against an unavailable prerequisite without an explicit compatibility plan. A branch being merged is not evidence its service is deployed.

PR titles and descriptions follow repository conventions. Lead with the concrete behavior and why it matters; include the validation and remaining risk a reviewer needs. Keep agent mechanics and long compliance inventories on the contract card. Use drafts until required checks are satisfied, and distinguish automated review from human approval.

## Migrations

**MIGRATE-ADDITIVE — expand, migrate consumers, then contract.** For independently deployed consumers, add a compatible shape, move readers/writers, verify all relevant deployed consumers have moved, then remove the old shape. Repo-wide search covers local callers, tests, seeds, and config; external consumers require a contract/deployment inventory too.

**MIGRATE-DUAL — transitional shapes agree.** Centralize conversion and test equivalent behavior across old and new entry points. If dual writes can diverge, specify the transaction, repair/reconciliation mechanism, and source of truth.

**MIGRATE-CONTRACT — name the live seam.** Record the shape added/removed, affected consumers and versions, prerequisite deployment, cutover signal, and cleanup condition. An obsolete interface with a live consumer is a blocker. Keep compatibility only as long as the actual support policy requires.

**MIGRATE-KEY — trace producers to consumers.** Cache invalidation, query keys, event names, flags, and storage keys must agree across the seam. Prefer a shared factory or generated contract within a build graph; across languages, use a versioned schema and contract test. Grepping is a lead, not proof that remote consumers are gone.

**MIGRATE-ROLLING — old and new processes coexist safely.** Check reads and writes with both versions during a rolling deployment. Add required fields compatibly before enforcing them; deploy code that can tolerate the transition before removing old columns or values. Bound schema locks and data movement. Test upgrading a representative prior schema, including existing rows, nulls, precision, foreign keys, and uniqueness. A clean database alone misses these failures.

Separate large backfills from short schema changes; make them resumable and observable when existing data warrants them. Decide rollback versus roll-forward before destructive steps. Do not run migrations against production without authorization.

**MIGRATE-IMMUTABLE — do not rewrite an applied versioned migration.** Check deployment history; add a new corrective migration when an earlier one may already have run. Squash/edit only unapplied migrations where the repository's migration policy permits it. Repeatable migrations follow their tool's explicit semantics, not this versioned-file rule.

## Gates

Derive commands from the lockfile, scripts, and CI. Focused tests are for iteration; final validation covers the full applicable build/test graphs, affected consumers, and project-required checks. Do not demand application e2e for a documentation-only change.

1. Establish the exact base and revision under test. Before starting a new branch, prefer a current remote base when remote access is available and relevant. Respect a requested existing branch.
2. Rebuild shared artifacts cleanly when stale output could affect consumers.
3. Run applicable type/lint checks, full unit/integration suites, production builds, and existing contract/dead-code checks.
4. Run relevant composed/runtime and browser journeys from the changed artifact. Use the full e2e suite when CI/repository policy requires it or the affected surface warrants it.
5. Record command, completion/exit status, counts and skips where available, revision, and any blocked or unrun checks. A failed or blocked required gate means not ready, never an implied pass.

Before pushing or merging, check the actual base currency. Fetch only when available/authorized; do not silently rebase a shared or published branch. Use the repository's merge/rebase policy, resolve conflicts, then rerun affected checks on the resulting revision. A stale offline remote ref cannot establish current main.

For UI changes, smoke the changed journey against the built stack: loading/empty/error/data states, relevant keyboard interaction, forms, and the actual network response. Report what was exercised and what could not run. A unit harness supplying missing production context is not a smoke test (`verification.md`).

A red check needs diagnosis: reproduce, compare with the base where feasible, fix introduced regressions, and report unrelated failures with evidence. Do not delete coverage, hide skips, or repeatedly retry an unexplained failure until it turns green. Preserve a legitimate baseline; never invent one.

## COMMIT-TRUTH — describe the actual diff

Use the repository's configured identity and commit convention. The subject describes this commit's behavior or purpose; do not reuse an unrelated subject over different diffs. Review staged paths and the staged diff before committing, keeping unrelated user work out.

No assistant attribution, generated-with footers, or co-author trailers. Do not create placeholder commits or push recoverability checkpoints unless the user requested that workflow. Local commits and remote actions are separate authorizations.

## Review and merge

Run an independent review for substantial or risky work when available; the scope and rigor follow `review.md`. Do not post review comments or open a PR merely because a local review was requested.

Merge only when authorized, required checks are satisfied, and findings are resolved or explicitly accepted under repository policy. An authorization persists for its stated scope; do not ask again for the same approved action. Surface a new decision when the scope or risk materially changes.

Never bypass hooks or branch protection, force-push a protected branch, or rewrite published history as a cosmetic fix. Follow repository policy and the user's specific authorization for any history mutation.

## Documentation

Update the documentation that the change makes inaccurate in the same commit: setup/config, contracts, operator behavior, migrations, and product usage as relevant. Do not add a new documentation tree when an existing one serves the purpose.

Operator-facing changes need the applicable runbook updates: startup/config, sync-to-async response/status contracts, new background work, failure/recovery behavior, schema/index changes, and auth changes. Cite symbols/behavior rather than brittle line numbers.

Describe shipped behavior; mark planned work explicitly. Do not fabricate traction, accuracy, security guarantees, or certification. Keep the final handoff focused on what changed, evidence, remaining limitations, and the authorized next action.
