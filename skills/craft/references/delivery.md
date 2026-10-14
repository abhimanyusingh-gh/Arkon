# Runtime readiness and recovery

Use for deployment-sensitive changes, new applications, performance constraints, and completion claims that depend on runtime behavior. Deployment actions still require the user's authorization; preparing and testing the artifact does not authorize releasing it.

## DELIVERY-READY — verify what will actually run

- Build and start the production artifact with the target runtime and representative configuration. A development server or unit suite is not evidence that the packaged application boots. See `dependencies.md` after runtime or dependency changes.
- Validate required config, migration ordering, dependencies, and root composition. Readiness should mean the instance can serve its intended traffic; distinguish liveness so a remote outage does not create restart storms.
- Identify which app/schema/API/event versions coexist during rollout. Test old reader/new schema and new reader/current schema when relevant. Run a migration from the prior deployed schema with representative existing rows; a clean empty database misses conversion and compatibility defects.
- Verify prerequisite capabilities are deployed before activating a consumer or feature flag. “Merged” and “available in production” are different states. Give transitional fallbacks an owner, observation, and removal condition.
- For feature flags, exercise on, off, and lookup failure at the backend effect and UI state boundaries. Disablement must stop new dangerous work while defining what happens to in-flight work.
- Check graceful shutdown: stop accepting work, drain or cancel within a bound, and leave leases/claims/messages recoverable. Test restart behavior for durable work.

## Performance and observability

Use a stated product target: expected data volume, concurrency, latency percentile, and resource/cost budget. Do not invent a benchmark result or add machinery without a need.

- Examine the real query plan, pagination, N+1 calls, serialization, and external-call fan-out on the main path. Test representative cardinality/skew; a one-row fixture cannot establish scale.
- Bound memory and work: batch/stream large results, cap uploads and response sizes, and specify backpressure for queues. Measure before claiming an optimization.
- Expose health and operation outcomes sufficient to detect a stuck queue, failed write, elevated latency, and unexpected spend. Use low-cardinality, privacy-reviewed dimensions (`observability.md`).
- Define an actionable alert and response owner for a new critical asynchronous failure mode. An error log without a recovery path is incomplete operation.

## DELIVERY-RECOVER — a release has an exit path

- State the rollback or roll-forward condition and procedure. Schema expansion may allow app rollback; a destructive migration may require recovery from backup or a forward fix. Never describe application rollback as undoing lost data.
- Keep backfills/resyncs resumable, bounded, and idempotent where existing data requires them. Separate them from a long schema transaction, reconcile totals, and retain evidence of failures. See `workflow.md` for migration immutability.
- Verify backup/restore or repair procedures when changing critical persistence. Use a safe environment and synthetic or approved data; never test destructive recovery against production without authorization.
- Prepare a short runbook: new config, rollout sequence, health signals, disable/rollback action, known limitations, and cleanup condition. Docs describe shipped behavior.

Return artifact/startup evidence, compatibility evidence, and any unrun checks on the contract card. For a change without runtime or deployment effects, state why these checks are not applicable.
