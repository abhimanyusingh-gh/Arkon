# Designing and building an application

Use for a new product or a feature spanning UI, services, data, or integrations. For a small local fix, keep only the relevant decisions. Start with the repository's existing architecture; introducing services, queues, frameworks, or generic engines requires an actual constraint they solve.

## APP-ACCEPTANCE — make the product executable

Turn the request into a short acceptance matrix before implementing. For each user journey, capture the actor, preconditions, action, observable result, failure result, and proof. Mark existing behavior that must survive. Separate a working feature from a stub, a mocked dependency, and an explicit deferral.

- Include the primary journey, unauthorized access, empty data, invalid input, and the relevant interruption or concurrency cases. Do not multiply a full cross-product where combinations have no distinct behavior.
- Trace each criterion to a live entry point and a test or reproducible observation. A list of completed files is not product completion.
- Resolve material uncertainty about product behavior with the user. Resolve ordinary implementation choices from repository patterns and evidence. Record an assumption and its consequence when proceeding is reversible.
- For a visual product, identify the design reference, responsive behavior, keyboard flow, and loading/error/empty/success states before replacing controls.

## APP-BOUNDARIES — choose ownership before abstractions

Draw only the boundaries needed to explain the change: entry point, use case, domain rules, persistence, and external systems. A compact table is enough.

| Boundary | Decide |
|---|---|
| Use case | Who is allowed to do what, and which invariant must hold? |
| Data | Who owns each fact, which writes are atomic, and what is the scope key? |
| API/event | Request/response schema, identity/version, errors, pagination, compatibility |
| UI | Server versus local state, invalidation, pending and failure transitions |
| External side effect | Deadline, retry budget, duplicate handling, recovery owner |
| Deployment | Which versions coexist, and which capability must be live first? |

Keep domain decisions independent of transport and persistence. Use concrete modules until multiple implementations or a genuine isolation/testing boundary justify a port. Avoid a generic workflow engine for one workflow, and avoid a new service when a module and a transaction satisfy the need.

## APP-DATA — specify semantics before storage

- Define valid state transitions, terminal states, mandatory relationships, uniqueness, and deletion/retention rules. Enforce critical invariants with database constraints or conditional writes as well as application validation.
- For derived values, specify units, decimal precision, rounding point, timezone, effective interval and endpoint inclusivity, null/zero/unknown distinctions, source precedence, and deterministic tie-breaks where relevant. Preserve these across serialization and display.
- Related displayed and computed values must use the same selected inputs. A report using one height for display and another for its computed ratio violates its contract even if both calculations are individually valid.
- State the source of truth; don't independently rederive the same policy in a migration, backend, and UI. Verify cross-field invariants with independent expected examples.
- Model concurrent transitions explicitly: version check, unique constraint, transaction, or compare-and-set. “Read then decide then save” needs a conflict policy.
- Design bounded reads and pagination with a stable order. Check representative query plans before adding speculative indexes. Read `authoring.md` for index rules and `workflow.md` for rolling migrations.

## APP-SLICE — prove one complete path before widening

1. Implement the smallest useful journey through real composition: entry point -> authenticated use case -> durable state or integration -> visible result. Check an uncertain external contract early using a safe fixture or sandbox.
2. Add the important failure path and prove an existing capability still works. Run focused checks before changing the next boundary.
3. Extend by independently reviewable behavior. Keep each intermediate revision internally consistent and backward compatible with deployed consumers.
4. Validate the composed application, not only leaf modules: root UI providers, actual configuration, packaged startup, real database behavior, and a representative end-to-end journey.

At each slice, report acceptance coverage and remaining work. Do not claim the application is complete while its primary path depends on an unimplemented adapter, fabricated data, or an unverified deployment assumption.

Before handoff, walk the acceptance matrix against running behavior and run `verification.md` plus the applicable delivery checks. Risk determines the depth of design and validation; document volume does not.
