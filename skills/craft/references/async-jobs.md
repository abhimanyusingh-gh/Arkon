# Background jobs

Anything that runs without a request: schedulers, pollers, queue workers, manual "run now" endpoints. Applies whenever the work can run on more than one instance or overlap itself, which is every deployed service.

## Single runner

**JOB-LEASE — a job that can run twice at once holds a datastore lease.** An in-process guard (skip-if-running flag, mutex) covers one process; a second replica, a rolling deploy, or a manual trigger walks past it. Overlap is a **blocker** when the job writes, retires rows, or spends money per unit of work; otherwise should-fix.

One row per job: `holder`, `expires_at`. Three operations, each one conditional update that reports rows changed, never read-then-write:

```text
acquire(job, holder, now, ttl)  SET holder, expires_at = now+ttl  WHERE holder IS NULL OR expires_at <= now  -> changed == 1
renew(job, holder, now, ttl)    SET expires_at = now+ttl          WHERE holder = :holder                     -> changed == 1
release(job, holder)            SET holder = NULL                 WHERE holder = :holder
```

- `holder` is a fresh random id per run, not a host name: a restarted instance must not inherit its predecessor's lease.
- Release is holder-conditional and runs in `finally`. A run that outlived its ttl and was taken over must not free the new holder's lease.
- Renew after every unit of work, **the last one included**, and stop the moment renew returns false. The ttl bounds a crashed holder, not a slow one.
- Renew immediately before any destructive follow-up (retiring rows, publishing results). A lost lease must never reach that step.
- The ttl is config, sized to a few units of work, never to the whole run. Job names are a const enum (`ENUM-CONST`) and each has a lease row seeded by migration.
- Finding the lease held is a normal skip: info level, returned as "not run". Not an error, not an alert.

## Gates

**JOB-GATE-ORDER — cheapest, side-effect-free gates first, the lease last.** Feature flag, then time window, then lease. A job that takes the lease and then finds itself switched off has blocked its peers for nothing.

- A flag lookup that throws means **off**, logged at error on every tick so it stays visible. Never default a failed lookup to on.
- The flag defaults off at the read site. Turning a feature on is a deployment decision.
- Re-check flag and window between units, not only at the start. A kill switch that waits for a long drain is not a kill switch.
- A manual trigger bypasses the window only, never the flag and never the lease.
- A gate skip logs at debug unless state changed (window just opened, flag just flipped). An idle poll every few minutes must not write an info line per tick.

## Queue

**JOB-QUEUE-ORDER — drain order is persisted data, and it is total.**

- One rank policy (an interface with one implementation) computes an integer at write time and the row stores it. Consumers order by `rank, id`; the id tiebreak makes the order total, so two workers never disagree.
- Unrankable rows (missing input) sort **last** with a maximum sentinel. Never null, never dropped.
- Every consumer of the queue uses the same order. A second stage that orders differently starves what the first stage prioritised.
- The index leads with the claim predicate, then rank, then id (`INDEX-COVERING`). A rank computed at read time cannot be indexed, so persist it. Never sort the population in memory.
- Re-rank queued rows when the upstream input changes, and write only when the rank actually changed. No second rank formula in a migration or backfill.

**JOB-FENCE — a claim is a token, and every write-back is conditional on it.** Claim one row at a time under a row lock that skips locked rows. Stamp a fresh random token and a claim expiry, and increment the attempt counter *at claim time*, so a crash burns an attempt. Every outcome write (complete, retry, defer, fail) is `UPDATE ... WHERE id = :id AND claim_token = :token` and returns whether it matched. False means superseded: log it, count it, stop. Never write anyway.

- An expired claim is reclaimable. Surface reclaims as a counter, not silence.
- Retiring or requeueing a row clears its token; that is what fences a slow worker out.
- The token never appears in a log line, a correlation id, or a metric tag.
- Attempts are bounded per window and windows are bounded, then the row goes terminal-failed with an alert. A row that can retry forever is a leak.

**JOB-RETIRE — rows the upstream no longer lists are retired, never deleted, and only after a complete crawl.**

- Retire means a status (obsolete) with flags and token cleared. History survives and revival is possible.
- "Complete" means every page was read and the lease was still held after the last one. Any error, partial page set, or lost lease retires nothing.
- An **empty** crawl retires nothing. Empty is indistinguishable from an upstream outage, and "retire everything" is the failure mode. Blocker if the guard is missing.
- Rows skipped for a data reason (missing or unrecognised field) still count as seen. Otherwise one bad field retires a live row.
- Retire only rows still queued. Terminal rows ignore later upstream updates, or the job's own write-back to the upstream re-queues what it just finished, in a loop.
- A revived row keeps its attempt and failure counters when the upstream data is unchanged and resets them only on fresh data. Otherwise retire-then-revive is a retry-budget reset.
- Retire in bounded batches, not one unbounded `IN` list.

## Outcomes

**JOB-OUTCOME — every unit ends in exactly one value of a closed outcome enum, and that value is the telemetry.**

- Values such as processed, retry, awaiting-input, failed, superseded. Retry-versus-terminal lives in the type, not in a string.
- One counter and one timer tagged by outcome. Tags are enum values only, never an id, an upstream value, or free text (`LOG-LENGTH`).
- One info line per unit: id, outcome, attempt, reclaimed flag, duration.
- Alert counters fire for terminal states and for a once-only stuck threshold (`==`, not `>=`, or it pages every tick).
- A backlog gauge makes a stalled queue visible without reading logs. Skips are counted by reason, with the reason as the only tag.
- A worker survives its handler: catch at the loop, log, continue, and let the claim expire. The failure handler is itself wrapped; failing to record a failure falls back to claim expiry, logged at error.

## Triggers

**JOB-TRIGGER — a manual "run now" endpoint is asynchronous, shares the lease, and is authorised.** It returns 202 after starting the run in the background and 409 when the lease or a manual drain is already held. It needs an admin-grade role: it spends money and bypasses the schedule. A synchronous trigger holds a request open for a backlog-sized run, times out, and orphans the run. If starting the background run throws, reset the "running" flag.

## Tests

**TEST-LEASE — lease semantics are proven against the real datastore.** A mocked repository cannot show the update is atomic. Cases: free lease acquires; held and live refuses; held but expired is taken over; acquire after release; **N contenders in parallel, exactly one winner, repeated for several rounds**; renew by the holder extends; renew by a displaced holder fails; release by a displaced holder does not free the current holder's lease; every job name has a seeded row.

**TEST-GATE — one test per gate, and each asserts everything downstream was not touched.** Flag off: window, lease and service untouched. Window closed: lease and service untouched. Lease held: service untouched. Plus: flag lookup throws means off and an error is logged; lease lost on renew stops the run and still releases; a gate flipping mid-drain stops it; a throwing unit logs an error and still releases.

Job-specific cases that earn their place: lease lost between pages stops before the next fetch; lease lost after the last page retires nothing; empty crawl retires nothing; an error on a later page retires nothing; lowest rank claims first with the id tiebreak; a stale token's write returns false; a revived row keeps its counters; the trigger returns 202 then 409.

## Reviewer checklist

1. Can this job run on two instances? Where is its lease row?
2. Is release holder-conditional and in `finally`? Is renew after the last unit?
3. Is the flag checked before the lease, and does a failed lookup mean off?
4. Is drain order `rank, id` from a persisted column with a covering index?
5. Does every write-back carry the claim token and handle a false result?
6. Can retirement run after an error, a lost lease, or an empty crawl?
7. Does every unit end in one enum outcome with a counter, a timer and one info line?
8. Are metric tags enum values only?
9. Is the manual trigger asynchronous, 409-aware and role-restricted?
10. Do the tests in the Tests section exist, against a real datastore for the lease?

Common misses: trusting the in-process skip annotation; ttl sized to the whole run; unconditional release; "seen" built from processed rows instead of listed rows; a second rank formula in a migration.
