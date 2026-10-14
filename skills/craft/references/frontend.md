# Frontend

Use the existing framework and design system. Interactive work also reads `accessibility.md`. Treat behavior, accessibility, and visual fidelity as parts of the same feature; split delivery only when each slice remains useful and safe.

## Design fidelity and completeness

Use the approved design as the target for content, density, layout, states, and responsive behavior. Identify the actual reference before redesigning; if none exists, follow established product patterns and make ordinary reversible choices.

- Enumerate the visible journey, including loading, empty, error, success, keyboard flow, and responsive variants. A missing backend capability is a contract gap to resolve, not permission to invent unrelated content.
- Reuse design tokens, typography, icons, and components. Verify consumed custom properties are defined and check all supported themes. Do not add speculative theme support.
- Preserve existing business behavior, state, accessibility, and selectors while changing markup. Replacing a design shell is not a reason to rewrite the domain logic.
- Compare changed surfaces with the reference at relevant viewports and states. Capture or describe meaningful deltas and limitations. Proportion the evidence to the change rather than requiring a DOM audit for a one-line fix.
- Keep styling in the repository's established system. Prefer shared tokens over repeated literals; use supported component variants and styling APIs. Runtime positioning or computed dimensions may legitimately need runtime styles.
- Diagnose cascade order, layers, specificity, and supported overrides before replacing a library component. Later insertion alone does not override every more-specific rule. Replacing an accessible primitive requires preserving its keyboard, focus, and state behavior.

Functional and visual passes can be separate for a large redesign, but both remain in the acceptance criteria. Do not require two agents or two PRs for every UI change. A functional slice includes visible focus and accessible interaction; those are not deferred polish.

## Server state and local state

One owner fetches/cache-manages a server resource per domain. Reuse the project's server-state library when present; do not introduce one for a single request without need. Avoid parallel hand-written loading/error/abort implementations for the same data.

Use cache keys that encode customer scope and all inputs affecting the response. Centralize key construction and align invalidation with every subscriber (`MIGRATE-KEY` in `workflow.md`). Clear or partition user-specific caches on identity changes.

Imperative transport is legitimate for bootstrap, streams, one-time downloads, presigned uploads, and worker contexts. Keep authentication, cancellation, retries, and errors consistent with the application; a one-use expiring URL need not become long-lived cached server state.

Keep form drafts and component-local UI state local until sharing/persistence is required. Use the existing store for state that needs it, with narrow subscriptions. Do not copy server records into a global store merely to display them or move every local flag into global state.

## State contracts

**STATE-CONTRACT — pending, absent, empty, error, and data are distinct.** Render initial loading, loaded-empty, loaded-data, and failure from explicit state. A truthiness test must not turn an empty result into an endless spinner. Expose an actual retry action when recovery is possible.

**STATE-REFETCH — background work preserves useful context safely.** Keep current data during refetch when it still describes the same authorized view, with a pending affordance. After a scope/identity change, clear foreign data immediately. For changed filters/pages, show previous data only when it is clearly labeled and actions cannot target the wrong rows.

**STATE-NODELAY — pending UI represents actual work.** Do not add arbitrary delays to synchronous work. A deliberate animation or interaction debounce has its own product purpose and must not conceal completion or create a fake network state.

**STATE-DRAFT — retained draft state and submitted state have different contracts.** Conditional forms may preserve hidden drafts for navigation, but serialize only the active, permitted branch. Never submit stale hidden notes or fields simply because they remain in a component state object. Test switch-away, switch-back, reset, and the actual saved payload; the backend also validates allowed fields.

**STATE-ASYNC — late responses cannot overwrite newer intent.** Cancel obsolete work or compare request/input versions before applying a response. A user changing selection, identity, document, or route invalidates earlier results. Prevent duplicate submits where relevant and preserve editable state on failure.

For AI-assisted edits, separate suggested/previewed values from committed values. When the product requires deliberate acceptance, saving is unavailable until acceptance/rejection resolves the preview. Label the state accessibly and test stale suggestions, reset, accept, reject, and save; parser validity alone does not authorize a consequential decision.

## Errors and validation

Choose presentation by where the user can act. Field errors belong with associated inputs and accessible descriptions; global/transient outcomes can use the existing toast layer; persistent surface failures need a stable message and retry path. Avoid duplicate announcements for one failure.

Never silently swallow a rejection or display success before the outcome is known. Keep entered data on a failed submission. Do not rely on a disabled button or a disappearing toast to explain every validation error. The backend enforces the invariant regardless of UI state.

## Bulk and optimistic mutations

**BULK-ATOMIC — the server contract states atomic or per-item outcomes.** Prefer an existing bulk endpoint when it can enforce the intended semantics. A client loop is multiple independent mutations; it cannot roll back committed server effects by restoring a local snapshot.

**BULK-PARTIAL — report partial success accurately.** With independent fan-out, settle and collect results, bound concurrency, then report successes and failures. A short-circuiting loop can leave an unknown tail; one total-failure toast misrepresents committed successes.

**BULK-ROLLBACK — undo only uncommitted optimistic state.** Use an atomic server operation, per-item rollback plus invalidation, or avoid optimistic bulk updates. Reconcile from the server after uncertain outcomes. Test a later item failing after an earlier one committed.

**BULK-IDEMPOTENT — repeating the action cannot repeat the business effect.** Reuse the logical operation identity across retries where required (`IO-IDEMPOTENT` in `integrations.md`). Do not key deduplication permanently on a set of IDs if performing a later distinct operation on the same records must remain possible.
