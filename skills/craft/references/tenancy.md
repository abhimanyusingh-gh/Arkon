# Scope isolation

The **scope key** is whatever partitions rows between customers — tenant id, org id, workspace id, realm, account id. Bind `<scope-key>` from the project and read every rule below against it. Projects with a nested partition (tenant → client org) have a *composite* scope key: every rule applies to the whole composite, not the outer half.

Read this before writing the query, not after review flags it.

## SCOPE-QUERY — every read and write carries the scope key

Every query, update, delete, aggregate, and count is constrained to the authorized scope. Enforce this in the query/repository or a verified datastore policy such as row-level security; a caller's prior lookup alone does not protect later writes. A reachable unscoped operation exposing another customer's data is a **blocker**.

- Include the full scope in predicates/policies. Predicate text order does not enforce isolation; choose index order from the actual query plan (`INDEX-COVERING` in `authoring.md`).
- Aggregations match on the scope key in the first stage, before any join or lookup. A join into an unscoped table re-widens the query — scope the joined pipeline too.
- Bulk, batch, export, report, and admin paths are not exempt. An unscoped bulk write is the worst version of this bug, not an acceptable one.
- With a composite scope key, filtering on the inner half alone is still a leak. `{ clientOrgId }` without `{ tenantId }` trusts that inner ids never collide across tenants.
- Cross-scope reads exist only as an explicitly named capability (`listAllScopesForSupport`), one function, authorization checked at its entry — never an optional parameter that defaults to unscoped.

## SCOPE-REPO — enforce at the lowest layer that can

Do not rely on N call sites remembering. Put the invariant where it cannot be forgotten:

- a repository layer taking the scope as a required first argument and injecting the filter; or
- a pre-save / pre-query hook on every model owning a scope key; or
- a verified datastore policy applied to the application's actual database role. A required scope field/write guard helps inserts but alone does not protect reads or cross-scope updates.

Enumerate the models and operations governed by the boundary being changed, including joins and indirect paths. A systemic guard change needs systematic coverage. Report other gaps without silently expanding a local task into unrelated rewrites.

## SCOPE-REGRESS — a re-introduced scope violation is a blocker

Once review has flagged a dropped scope key on a file, every later round re-checks that file specifically. Re-introducing it is a blocker, and the fold must add the structural guard from `SCOPE-REPO` — not just re-add the filter to the one query. A defect that comes back is evidence the fix was at the wrong layer.

## SCOPE-RESOLVE — one resolver, at the edge

Scope is resolved once, in middleware, from the authenticated principal — never from a request body, query string, or path segment the client controls. A handler that accepts a scope id as a parameter is accepting a client-supplied authorization decision.

- Downstream code reads the resolved scope from request context and never re-derives it.
- **Reject rather than default** when resolution fails. No "fall back to the first org", no "if absent, use the only one".
- Where a path segment does name a scope, a dedicated guard asserts the authenticated principal owns that segment before the handler runs — resolution and ownership are two checks, not one.
- The resolved scope is stamped onto every created record at the boundary, not by each writer remembering to pass it.

## SCOPE-NOOP — verify the helper's implementation, not its name

A shared authorization helper that returns without checking for some class of caller makes every call site read as guarded when it is not.

- A permission helper with `case SERVICE_ACCOUNT: break;` — commented as "service accounts are assumed pre-authorized" — routes every `Actor`-typed authorization overload through a check that can never throw for service callers. Three endpoints inherit the silent no-op without a line of their own that says so.
- When a caller class is exempt, the exemption belongs at the call site where it's visible in review, not buried in a shared helper where it's inherited silently.

## SCOPE-NARROW — filters narrow the boundary, they never widen it

When an endpoint accepts client-supplied filters alongside an actor-derived boundary, the effective scope is the intersection. A filter must never be the thing that grants access.

- A caller with no authorized boundary is rejected unless an explicit privileged capability grants the requested cross-scope action. A supplied filter alone cannot create permission.
- A lookup endpoint taking `?patientId=` chosen by the caller lets the caller name its own scope. Invert it: the boundary derives from the authenticated actor, and filters only intersect within it.

## SCOPE-OPAQUE — not-found and not-permitted are indistinguishable

For object lookup, use the project's non-disclosure policy so missing and foreign objects do not reveal cross-scope existence. A common policy returns the same not-found response for both. Preserve the authentication contract (such as missing/expired credentials) separately.

- The authorization failure is converted to not-found at the boundary, never propagated as a distinct status.
- Honest tradeoff: a legitimate caller debugging a permissions problem sees not-found rather than forbidden.

## SCOPE-PATH — object storage, file paths, and cache keys are scoped too

Bind object storage and export access to verified scope ownership, using scoped keys or equivalent trusted ownership metadata/policies. A scope segment is organization, not proof of permission. Authorize before issuing a narrowly scoped, expiring signed URL; never infer ownership solely from a caller-supplied path or opaque id.

Cache and query keys include the scope key too, or one customer's response is served to another on a shared key.

## SCOPE-TEST — the negative test is the test

Every scoped surface ships a test that seeds two scopes and asserts the second cannot read, list, count, update, or delete the first's rows — per surface, not once per project. A positive test proves the feature; only the negative test proves the isolation.

- Seed the second scope with data that *would* match the filter if the scope key were dropped. A negative test against an empty second scope passes with the bug present.
- Cover the list endpoint, the detail endpoint, every mutation, every export, and every aggregate separately — they are separate queries and they fail independently.
- Dependency and cascade checks are exhaustive or they are wrong: counting 4 of 15 dependent tables reports "safe to delete" for a record that is not.
