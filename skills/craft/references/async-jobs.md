# Background jobs

Schedulers, pollers, queue workers, and manual "run now" endpoints. Apply exclusivity rules where overlap would violate an invariant; parallel workers are valid when their claims and side effects are safe. First identify the execution scope, delivery guarantee, and effects that must survive a crash.

## Single runner

**JOB-LEASE — enforce exclusivity at the scope that needs it.** An in-process guard covers one process. Use an existing scheduler/queue guarantee, datastore lease, or equivalent distributed coordination when a second replica or manual trigger could violate correctness. A global lease is unnecessary for a queue designed for parallel claimers. Unsafe overlap causing duplicate charges, conflicting writes, or retirement is a **blocker**.

For a datastore lease, one row per exclusivity scope: job name and, for tenant-local work, scope key. Store `holder`, `expires_at`; use the datastore clock for comparisons and expiry calculation. Three atomic conditional updates report rows changed, never read-then-write:

```text
acquire(job, holder, now, ttl)  SET holder, expires_at = now+ttl  WHERE holder IS NULL OR expires_at <= now  -> changed == 1
renew(job, holder, now, ttl)    SET expires_at = now+ttl          WHERE holder = :holder AND expires_at > now -> changed == 1
release(job, holder)            SET holder = NULL                 WHERE holder = :holder
```

- `holder` is a fresh random id per run, not a host name: a restarted instance must not inherit its predecessor's lease.
- Release is holder-conditional and runs in `finally`. A run that outlived its ttl and was taken over must not free the new holder's lease.
- Renew during long units with a heartbeat, or bound their timeout comfortably below the ttl; renewing only after a unit permits takeover during it. Check ownership after every unit, **the last one included**. A failed or uncertain renewal stops new work; an expired holder cannot revive its lease.
- A successful renewal is not a fence: the holder can pause immediately afterward and resume after takeover. Protect destructive database writes by checking and locking live ownership in the same transaction, using a consistent lock order, or by a monotonically increasing fencing generation checked by the target. External effects require the protections in `JOB-EFFECT` below.
- The ttl and renewal interval are config, sized from bounded work duration and heartbeat margin. Use stable typed job names (`ENUM-CONST`); create lease rows safely by migration or atomic initialization, never a competing insert/read sequence.
- Finding the lease held is a normal skip: info level, returned as "not run". Not an error, not an alert.

## Gates

**JOB-GATE-ORDER — cheapest, side-effect-free gates first, the lease last.** When these gates exist: feature flag, then time window, then lease. A job that takes the lease and then finds itself switched off has blocked its peers for nothing.

- A flag lookup that throws means **off**, logged at error on every tick so it stays visible. Never default a failed lookup to on.
- New optional or costly automation defaults off at the read site. Essential existing work follows its documented operating policy; adding a flag must not silently disable it.
- Re-check flag and window between units, not only at the start. A kill switch that waits for a long drain is not a kill switch.
- A manual trigger bypasses the window only, never the flag and never the lease.
- A gate skip logs at debug unless state changed (window just opened, flag just flipped). An idle poll every few minutes must not write an info line per tick.

## Queue

**JOB-QUEUE-ORDER — define queue order and fairness explicitly.** For a priority queue:

- One shared rank policy computes an integer at write time and the row stores it, unless the datastore can index the required expression. Consumers order by `rank, id`; the id tiebreak makes the requested order total. Concurrent skip-locked claims can finish out of order; strict execution order needs separate coordination.
- Unrankable rows (missing input) sort **last** with a maximum sentinel. Never null, never dropped.
- Consumers of the same priority policy use the same order. Define aging or another fairness mechanism if high-priority arrivals could starve older work; a total order alone does not prevent starvation.
- Design the claim index from the actual predicate and query plan, including the scope key for scoped work, then rank and id where supported (`INDEX-COVERING`). Never sort an unbounded population in memory.
- Re-rank queued rows when the upstream input changes, and write only when the rank actually changed. No second rank formula in a migration or backfill.

**JOB-FENCE — a claim is a token, and every write-back is conditional on it.** Claim atomically: in SQL, a row lock that skips locked rows; elsewhere, the datastore's equivalent conditional mutation. Stamp a fresh random token and a claim expiry, and increment the attempt counter *at claim time*, so a crash burns an attempt. Commit the claim before external work; do not hold a database transaction open across a network call. Every outcome write (complete, retry, defer, fail) filters on scope, id and claim token and returns whether it matched. False means superseded: log it, count it, stop. Never write anyway.

- An expired claim is reclaimable. Surface reclaims as a counter, not silence.
- Retiring or requeueing a row clears its token; that is what fences a slow worker out.
- The token never appears in a log line, a correlation id, or a metric tag.
- Bound retry rate and work per window, and define exhaustion and operator recovery. Finite workflows eventually become terminal-failed with an alert. A product requiring eventual delivery may retain durable pending work with backed-off retries and actionable stuck/backlog signals; do not silently discard that obligation at an arbitrary attempt count. Unbounded tight retries are a leak.

**JOB-EFFECT — claim tokens fence datastore write-backs, not external effects.** A worker may charge, send, or publish, then crash before recording success. A timed-out request may also have succeeded remotely. Reclaims and retries must not repeat an irreversible effect.

- Use a target-supported idempotency key stable for the logical operation across retries and reclaims, or deduplication committed atomically with the effect at the target. A fresh claim token is not an idempotency key. Include scope and operation/version where necessary; do not include personal content. Add target-enforced fencing when stale-holder ordering matters; fencing alone does not deduplicate replay of an already completed operation.
- When recording a state change and publishing an event, commit an outbox entry with the state change, then dispatch with deduplication. An outbox provides durable delivery, not exactly-once consumption.
- Without idempotency, replay only when a definitive operation-status lookup confirms no effect and no in-flight attempt. Otherwise ambiguous completion becomes a reconciliation outcome before another attempt. Do not promise exactly once from a lease.

**JOB-RETIRE — rows the upstream no longer lists are retired, never deleted, and only after a complete crawl.**

- Retire means a status (obsolete) with flags and token cleared. History survives and revival is possible.
- "Complete" means every page was read through the upstream's authoritative snapshot/cursor contract and ownership is still valid at each retirement transaction. A changing or filtered listing is not automatically a complete snapshot. Any error, partial page set, or lost lease retires nothing.
- An **unconfirmed empty** crawl retires nothing: "retire everything" is the failure mode. If an authoritative, successful snapshot can legitimately be empty, define how that is confirmed and allow retirement through that path. Test both legitimate empty and failed/ambiguous empty responses.
- Rows skipped for a data reason (missing or unrecognised field) still count as seen. Otherwise one bad field retires a live row.
- Retire only eligible queued rows. Terminal rows ignore the job's own write-back and unchanged upstream data; a genuinely new input revision may create new work according to the product contract. Track the processed revision rather than permanently ignoring all updates.
- A revived row keeps its attempt and failure counters when the upstream data is unchanged and resets them only on fresh data. Otherwise retire-then-revive is a retry-budget reset.
- Retire in bounded batches, not one unbounded `IN` list.

## Outcomes

**JOB-OUTCOME — every unit ends in exactly one value of a closed outcome enum, and that value is the telemetry.**

- Values such as processed, retry, awaiting-input, failed, superseded. Retry-versus-terminal lives in the type, not in a string.
- One counter and one timer tagged by outcome. Dimensions are bounded, non-sensitive values, never a record id, raw upstream value, or free text (`LOG-LENGTH`).
- One info line per unit: id, outcome, attempt, reclaimed flag, duration.
- Alert on terminal states and threshold crossings. Persist a deduplication marker or use the alerting system's grouping; `==` alone can miss a threshold crossed between observations or page again on a retried observation.
- A backlog gauge makes a stalled queue visible without reading logs. Skips are counted by reason, with the reason as the only tag.
- A worker survives its handler: catch at the loop, log, continue, and let the claim expire. The failure handler is itself wrapped; failing to record a failure falls back to claim expiry, logged at error.

## Triggers

**JOB-TRIGGER — an accepted run has durable ownership and visible status.** Authorise a manual trigger for its effects; a schedule-bypassing administrative drain generally needs an admin role. Use the same coordination as scheduled work.

- Return 202 only after a durable job record has committed or the durable queue confirms acceptance, with a run id and status location. A request-thread executor submission alone can lose accepted work on deploy or crash.
- Decide duplicate behavior explicitly: return the existing run for an idempotent request, or 409 for a conflicting singleton run. Make that decision atomically across replicas; an in-process "running" flag cannot establish it.
- Expose accepted, running, completed, failed, and cancelled states as applicable, with timestamps and a safe failure code. Separate trigger acceptance from successful completion. A crash must leave work reclaimable or observably failed, never permanently "running".
- Bound queue capacity, execution time, and shutdown drain. Cancellation stops new effects; it does not undo a completed external effect. If enqueue fails, report failure and release any reservation.

## Tests

**TEST-LEASE — lease semantics are proven against the real datastore.** A mocked repository cannot show the update is atomic. Cases: free lease acquires; held and live refuses; held but expired is taken over; acquire after release; **N contenders in parallel, exactly one winner, repeated for several rounds**; live holder renews; expired and displaced holders cannot renew; displaced release does not free the current holder's lease; lease initialization is safe. Also pause a holder past expiry and prove its destructive write is rejected after takeover. Control clock/expiry deliberately rather than relying on arbitrary sleeps.

**TEST-GATE — one test per gate, and each asserts everything downstream was not touched.** Flag off: window, lease and service untouched. Window closed: lease and service untouched. Lease held: service untouched. Plus: flag lookup throws means off and an error is logged; lease lost on renew stops the run and still releases; a gate flipping mid-drain stops it; a throwing unit logs an error and still releases.

Job-specific cases that earn their place: lease lost between pages stops before the next fetch; lease lost after the last page retires nothing; unconfirmed empty and a later-page error retire nothing; lowest rank claims first with the id tiebreak; a stale token's write returns false; a revived unchanged row keeps its counters; a crash after an external effect does not repeat it; a 202-accepted run survives worker restart; duplicate triggers follow the declared contract; status reaches a terminal state.

## Reviewer checklist

1. Which effects need exclusivity, and what enforces it across instances?
2. Are expiry, renewal and release correct? Can a paused holder still perform a destructive effect?
3. Where a kill switch applies, is it checked before the lease and does lookup failure stop automation?
4. Is queue order indexed and consistent with the declared priority/fairness policy?
5. Does every write-back carry the claim token and handle a false result?
6. Can retirement run after an error, a lost lease, or an unconfirmed empty crawl?
7. Does every unit end in one enum outcome with a counter, a timer and one info line?
8. Are metric dimensions bounded and non-sensitive?
9. Is acceptance durable, authorised, duplicate-aware, and backed by observable run status?
10. Are the applicable failure cases tested, against the real datastore when implementing leases/claims?

Common misses: trusting an in-process skip annotation; renewal after a long unit only; treating a lease as an external-effect fence; unconditional release; "seen" built from processed rows instead of listed rows; returning 202 before durable enqueue.
