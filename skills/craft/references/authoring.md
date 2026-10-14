# Authoring production code

Apply to the code being changed. Follow the repository's language and framework conventions; the invariant matters more than a particular folder structure or syntax.

## Before writing any code

1. Identify the acceptance criteria, affected callers, and important edge cases. For substantial work, state a short plan before implementation; a local fix can keep this in working notes.
2. State what existing behavior must survive and which behavior intentionally changes.
3. **Debloat on touch** — inspect adjacent code for duplication and misleading dead paths. Fix directly relevant defects; flag unrelated cleanup rather than expanding the task.
4. **YAGNI** — nothing beyond what the issue requires. No speculative props, no single-caller indirection, no "while I'm here" expansions.
5. Keep responsibilities clear; introduce abstractions when they protect a real boundary, not to create a layer for each function.
6. **DRY** — search for the existing helper before writing a new one.

**TOUCH-BLAST — a change alters behavior only where intended.** When restoring, relocating, or retyping a shared field, compare its mappings and consumers against the base revision. Preserve unrelated semantics, including units, null handling, serialization and defaults. A shared type change may require mechanical consumer edits; an empty diff is not the only valid proof. Explain intentional behavior changes and verify the important unaffected paths. Adjacent cleanup does not authorize deleting live capabilities.

Reactive bug-fixing after merge is the failure mode this replaces.

## Code reuse

1. Search the codebase for an existing implementation covering the use case.
2. Prefer extending or parameterizing over cloning.
3. Share policy that must evolve together; preserve boundaries for different use cases and contracts.
4. Repeated logic is a signal to compare semantics before extracting. A shared primitive helps when it removes a real source of drift, not merely similar syntax.
5. For substantial work, report the meaningful reuse decision on the evidence card.

**REUSE-WRAPPER — an indirection needs a purpose.** Collapse pass-through wrappers that add no policy, ownership, compatibility or isolation benefit. A port satisfying a genuine integration boundary can be useful even when its current implementation forwards one call.

**REUSE-SIBLING — avoid competing clients for the same contract.** Search the endpoint before adding a consumer; reuse the canonical request/cache/error policy. Distinct adapters or projections can be legitimate when their contracts differ, but must not silently disagree about the wire shape.

**REUSE-CONTRACT — response types have compatibility consequences.** Reuse a schema when endpoints intentionally share one contract; use separate DTOs when they evolve independently. Similar fields alone do not justify coupling public contracts or exposing the persistence model.

## Layering

- **Domain** — business types and transformations independent of transport, framework lifecycle and persistence effects.
- **Application** — use cases composing domain behavior and required persistence/integration boundaries.
- **Adapters (outbound)** — API clients, persistence, integrations.
- **Adapters (inbound)** — components/controllers translating input and presenting results; authoritative business rules stay in the owning use case/domain.

**LAYER-PORT — keep integration policy out of presentation.** Follow the framework's loader/query/use-case pattern; avoid raw clients scattered through components. A use-case hook is one frontend implementation, not a requirement for every stack.

**LAYER-LEAK — localize provider-specific policy.** Keep vendor formats, client options and error translation in the adapter. Use a port/capability boundary where it prevents provider switches from spreading through domain steps; do not erase a provider distinction that the product contract genuinely needs.

**LAYER-GOD — avoid one orchestrator owning every implementation detail.** Separate independently changing parsing, policy and I/O when the method becomes hard to reason about. A small explicit branch or cohesive state machine does not automatically require a strategy framework.

## Dead code

**DEAD-EXPORT — avoid speculative public surface.** New internal exports need a consumer or an explicit contract reason. Before removing existing exports, account for public package consumers, framework discovery, reflection, generated wiring and plugin contracts that a local import search may miss. Avoid barrels that add no useful boundary.

**DEAD-CAPABILITY — an unwired capability is not dead code.** When `<deadcode>` flags something, classify it before deleting.

**Delete** when it is *scaffolding*: a speculative export you or a recent PR added, a barrel nothing imports through, a wrapper that adds no behaviour, an abandoned duplicate of a live path, a flag whose feature already shipped.

**Wire it** when it is *capability*: it implements behaviour the spec, design source, issue, or API contract requires, and the only thing missing is the call site. Deleting it deletes the feature. In that case, in the same PR: wire it to its real consumer, cover it with a test, and say so in the PR body.

The test: does the current product contract require this behavior? If yes, the defect is missing wiring. Do not delete it to satisfy a dead-code tool. Credentials in the environment alone do not prove an integration is required or authorize using it.

**A clean grep answers "is this read today," not "does the domain require this."** A field with no current reader may still be load-bearing — for a consumer that doesn't exist yet, or for a distinction the code has no other way to make. "Verified zero consumers" is evidence for the usage question only, and is routinely presented as if it settled the semantic one. Before deleting a domain field, state what it *means* and what becomes unrepresentable without it: a nullable response field can't tell an empty text message from an image carrying no text without a `type` alongside it. Deleting a field to avoid writing a second mapper is the same defect from the other direction — two adapters parsing two wire formats into one domain type is what adapters are for.

If the contract remains unclear after reading callers, requirements and history, preserve the capability and raise the uncertainty; continue independent work.

## Enums and literals

**ENUM-CONST — model finite variants with the stack's existing type mechanism.** Reuse native enums, sealed types, discriminated unions, schema enums or constant-derived types as appropriate. Do not replace an established language enum with a TypeScript pattern. A const object plus derived type is one TypeScript option:

```ts
export const ITEM_STATUS = { draft: "draft", approved: "approved" } as const;
export type ItemStatus = typeof ITEM_STATUS[keyof typeof ITEM_STATUS];
```

**ENUM-IMPORT — consume the canonical variant type.** A component retyping a set already exported by the design system creates another source of truth. Validate unknown wire values before converting them into a trusted variant.

**ENUM-GROUPED — share repeated subset policy.** A terminal-status predicate or set belongs beside the state model when multiple callers need that same definition; avoid speculative groups with no consumer.

## Complexity signals

| Signal | Threshold |
|---|---|
| Function length | >50 LOC → inspect responsibilities; >100 → consider decomposition, accounting for language and data-heavy code |
| File length | >400 LOC for one concern → split candidate |
| Conditional chain | 4+ `else if` branches, or 6+ `switch` cases → lookup table / strategy map |
| Parameters | 5+ positional → options object; 8+ → smell regardless of shape |
| Nesting | past 4 levels → guard clauses / early return / extract helper |
| Growth over time | touched-and-grown in 3+ recent PRs → cost-of-extension is climbing, call it out |
| Mixed concerns | parsing + validation + persistence + side effects in one function → decompose |
| Implicit state | long function threaded with mutable locals and flags → extract pure functions |

These are review prompts, not automatic findings. Generated code, schemas, dispatch data and cohesive state machines may legitimately exceed them. A finding names the maintenance/correctness problem and a useful decomposition.

## Naming

**NAME-FULL — choose clear names in the repository's vocabulary.** Prefer recognizable domain terms over invented abbreviations. Established abbreviations such as URL, HTTP or a local domain term need not be expanded. Fix ambiguous names on the changed path; do not rename unrelated APIs or files merely to enforce a preference.

**NAME-TAXONOMY — reuse the word for the same concept.** Check existing usage before introducing a second spelling. Verify that terms such as user/member or archive/disable actually mean the same thing before unifying them; different domain concepts need different names. Plan broad renames as contract changes.

**NAME-SHAPE — preserve meaning across layers.** Follow each boundary's established conventions, such as SQL snake_case and JSON camelCase, with one explicit mapping. Avoid unexplained semantic renames and verify units/nullability as well as spelling.

**NAME-CASING — one casing per surface.** Enum values, route segments, query keys, and test ids each pick one convention and never mix. A value written `PartialItem` in one file and `partial_item` in another is two values as far as any datastore is concerned, and queries silently miss rows.

## Configuration

**CONFIG-DAY-ONE — distinguish policy, operational tuning and constants.** Give real operational tunables one validated source from their introduction. Do not add a database/config service for every number: fixed protocol values, mathematical constants and contract variants may be named code constants. Weights/rates that operators or effective-date rules must change need an appropriate versioned source.

| Category | Storage |
|---|---|
| Externally-mandated rates, thresholds, and deadlines that change on an effective date | Auditable effective-period data/config; preserve the version used for prior results |
| Per-scope operational tuning (approval thresholds, retention windows, batch sizes) | Authorized scope-specific configuration; use the existing configuration store |
| Process tunables (retry backoff, poll intervals, timeouts, cache TTL) | config file / env |
| Safety guards (max batch, max response size) | config file |

*Not* tunables: API-contract enums (interface boundaries), sentinel values, branded-type carriers, file paths, table and collection names.

**CONFIG-FAIL-CLOSED — required production configuration has no unsafe fallback.** Credentials, signing/encryption keys, mandatory identity/provider settings and other values required for safe operation must fail startup or prevent the affected feature from starting when missing/invalid. Report the key and safe reason, never its value. Development/test defaults are explicitly profile-gated and cannot silently reach production. Safe operational defaults such as a bounded batch size are allowed, centralized and range-validated; document their behavior. An optional safety gate's lookup failure disables that feature rather than authorizing work (`security.md`).

**CONFIG-FETCH — user-data config comes from the backend; the frontend never mirrors it.** Two categories of frontend constant:

- **A — user-data config** (option lists, master data, rates, workflows, classifications, role assignments): must be fetched. Never a static frontend file mirroring a backend seed — two sources of truth that drift the moment either side changes.
- **B — API-contract enums** (status values, wire-format identifiers, error codes): use the shared/generated schema or the project's native finite-value type; verify wire compatibility. Do not add a fetch solely to obtain immutable protocol variants.

Every PR adding a frontend constant answers: user-data or API contract? Never dual seeds.

**CONFIG-DERIVED — if a typed constant already enumerates the set, derive from it.** A local array re-listing valid tab names beside an existing route-map constant is a second source of truth.

## URL / URI abstraction

**URL-PROVIDER — reuse canonical route and integration construction.** Prefer the framework's named routes, generated client, or existing typed URL builder over repeated path construction. Keep caller routes, server registrations and external base URLs owned at their appropriate boundaries; these are possible homes, not three mandatory new modules:

- Frontend callers (API client, `fetch`, image sources, event streams, sockets) → the frontend's URL provider for that domain.
- Backend route registrations → the backend's route-URL provider for that domain.
- External services (third-party APIs, identity providers, cloud endpoints) → the backend's integration-URL provider for that service.

Add new routes to the existing owning mechanism and update consumers. URL construction does not validate an untrusted destination; apply `security.md` before redirecting or fetching.

**URL-ENFORCE — layered enforcement; a custom checker must understand the constant it mandates.** Typed providers catch within-side drift at compile time, reviewers grep the diff on URL-touching PRs, and e2e catches cross-boundary drift at runtime. That is the default stack and it needs no extra tooling.

Prefer existing type/schema/lint tooling before adding a custom checker. One may be worthwhile for an important otherwise-unchecked invariant, such as a client/server seam or architectural boundary. If you write one:

- It must resolve the *typed constant*, not just string literals. A checker matching only `"/api/items"` will flag the provider constant this skill mandates as a violation and block the correct fix. This has happened.
- It ships with its own tests, including one asserting the compliant typed form passes.
- It reports file and fix, never just a count.
- It is owned. When it blocks a correct change, the checker is the defect: fix or delete it in that PR. Never work around it by reverting to the string literal.

## Style

Prefer clear code and explain non-obvious reasons: a hidden invariant, compatibility workaround, external constraint, or important safety boundary. Follow the repository's public API/documentation conventions. Avoid comments that narrate each statement or claim correctness without evidence.

Temporary workarounds need a useful issue/removal condition when applicable; an unowned TODO is not a completion claim. Do not add review-process narration to product code.

Use named types/constants for repeated semantic values rather than explaining the same literal at each call site.

**Test names are self-documenting.** Banned in test and suite names: issue or PR numbers, internal bug nicknames, PR scaffolding ("post-rebase", "PR 2 follow-up"), anything meaningful only inside the current review thread. A reader six months out must understand the locked-in behaviour from the name alone.

## Type safety

**BRAND-SCOPE — use domain types where they prevent a real mix-up.** Prefer native value types such as UUID, Money, Instant, enums, records or validated wrappers where the stack supports them. In TypeScript, a brand can distinguish interchangeable-looking identifiers; a raw string is not automatically a defect.

1. Reuse the existing type before creating another. Distinguish scope id, user id and document id when accidental interchange is plausible; branding all three as one generic UUID does not distinguish them.
2. Use the native finite-value mechanism for variants (`ENUM-CONST`). Preserve unit, precision and timezone meaning for domain values.
3. Validate untrusted input at the boundary before constructing the trusted type. A cast or brand assertion alone proves nothing about format, authorization or customer membership.
4. Follow the ORM/schema's supported value mapping; validate conversions rather than assuming every persisted field must become a raw primitive first.

Place types with their owning domain according to repository conventions. Do not create a file, wrapper or public export per primitive without a concrete benefit. Type safety supplements runtime scope and authorization checks; it cannot replace them.

## Database

**INDEX-COVERING — verify how the actual query is served.** Inspect existing indexes and a representative query plan before adding another index. Consider expected cardinality, skew, filtering, sort, pagination and write cost. A new finder method does not necessarily require a new index, and a covering/index-only scan is not required for every query.

- Tenant queries retain the full scope predicate (`tenancy.md`). A scope-leading compound index is often appropriate; choose key order from the datastore's equality/range/sort behavior and actual plan, not a selectivity slogan alone.
- Extra index columns can support sorting, covered projections, or left-prefix queries; their absence from the filter does not automatically make an index unusable. Partial/filtered and included-column indexes have dialect-specific rules.
- Computed sorts may use supported expression/function indexes or generated columns if the query expression and datastore constraints match. Otherwise persist the derived value consistently or bound the candidate set before sorting. Never sort an unbounded population in memory.
- Reuse an index for compatible paths where the plan supports it. Avoid N+1 reads as well as unindexed reads; an index does not remove network round trips.
- Verify stable pagination and tie-breaks with realistic data. A small-table sequential scan may be correct; do not infer a production latency target from one fixture.
- Dropping or renaming an index is a deliberate migration — surface it.

**LOCK-MINIMAL — serialize the invariant with the smallest correct mechanism.** State the competing operations and choose a constraint, conditional write, transaction/isolation level or explicit lock supported by the actual datastore/version. A transaction does not by itself serialize read-then-write, and locking an existing row does not necessarily lock a missing key or range. Gap/predicate locks vary by dialect, index and isolation level; do not infer one database's behavior from another. Use a unique constraint/upsert for create-if-absent where appropriate, and handle conflicts/deadlock/serialization retries within a bound. Keep lock order consistent and network calls outside lock-holding transactions. Prove the competing path with `TEST-CONCURRENCY` in `testing.md`.

Avoid backfill machinery when there is genuinely no existing data to transform. Development, preview and staging data may still exist before launch; establish that fact rather than assuming every pre-production table is empty. When data needs conversion or repair, use the bounded, resumable and auditable migration/recovery approach in `workflow.md` and `delivery.md`.

Backfill and real-time write paths must preserve the same derivation policy; share that implementation where applicable and test both entry points with independent expected examples.

## Resource boundaries

Use the gateway for generic request throttling and the owning service for business quotas, expensive-action limits or bounded concurrency it can actually measure. Reuse platform mechanisms; do not add a local limiter that claims distributed enforcement across replicas. See `security.md` and `integrations.md` for boundary and budget requirements.
