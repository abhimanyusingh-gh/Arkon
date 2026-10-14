# External calls, events, and consistency

Use when crossing a process boundary or combining durable state with a side effect. Background ownership and claim fencing live in `async-jobs.md`; hosted-model specifics in `llm-calls.md`.

## IO-BUDGET — one bounded failure policy

- Define connect/read/overall deadlines and cancellation appropriate to the operation. Propagate the remaining request/job budget; a retry must not restart an unlimited clock.
- Retry only classified transient failures, with capped backoff and jitter and respect for server delay hints within the deadline. Count SDK, client, queue, and job retries together. Treat permanent authorization/schema failures as terminal until something changes.
- Record the maximum attempts and consequence for each side effect. Timeouts can mean “completed but reply lost”; do not translate uncertainty into a safe-to-repeat result.
- Bound concurrency, page sizes, payloads, and queued work. Decide what happens under pressure: reject, defer, or shed optional work. Use circuit breaking only when its failure/recovery behavior solves a demonstrated need.
- Normalize provider errors into a stable application outcome without losing safe diagnostic codes and correlation. Do not leak provider payloads or free-text exception messages.

## IO-IDEMPOTENT — duplicates cannot repeat the business effect

- Assign an operation key scoped to the actor/customer and intended action. Where supported, pass it to the target; record the request identity and result so the same key with different input is rejected.
- Enforce uniqueness or conditional transitions in the datastore. A local “already running” flag and a preflight lookup cannot prove exclusivity across replicas.
- Process the event's immutable identity and version, not “the latest” related record. Rapid events can otherwise process one record twice and skip its predecessor.
- Define stale, duplicate, and out-of-order behavior. Use a version/sequence check or an inbox record where needed. An event timestamp alone may not provide total order.
- Test a repeated event and a lost response after a committed effect. Distinguish exactly-once business effects from at-least-once delivery; do not promise either without the mechanism.

## IO-CONSISTENCY — make the crash window explicit

Write the local state transition and its transaction boundary before adding a remote action. If the process crashes between database commit and event publication, what makes the work eventually complete?

- Use the repository's transaction/after-commit mechanism when it is sufficient. For durable delivery across independent systems, use an outbox/inbox or an existing equivalent, with retries and duplicate handling. Do not hold a database lock across a long remote call.
- Multi-system work needs an explicit recovery state, compensating action, or reconciliation path. A catch block cannot roll back a remote effect that already committed.
- Define ack/nack and poison-message handling for consumers. Acknowledge after the durable state required for recovery exists, bound redelivery, and expose terminal failures for operators.
- Test the important crash window, not only the all-success path. Use the real datastore for atomicity and contention claims; a mocked transaction proves none of them.
- A merged producer change may not be deployed. Validate the actual available contract before activating a consumer; see `delivery.md`. Compatibility fallbacks need an owner and a removal condition, not permanent silent guessing.
