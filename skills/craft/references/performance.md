# Performance

Use for latency, throughput, memory, load, cache and scale claims, and for slow queries. Start from a stated product target: expected data volume, concurrency, latency percentile, and resource or cost budget. Without a target there is no regression to detect. Do not invent benchmark results, and do not add caching, batching or indexes without a measured need.

## PERF-MEASURE — measure before and after

- Baseline the base revision on a representative workload with realistic data cardinality and skew. A one-row fixture cannot establish scale.
- Profile to find the cost before changing code. Name the hot path from the profile, not from intuition.
- Repeat runs and report variance. Use the same environment, data, configuration and load for both sides.
- Record the revision, command, dataset identity and container or hardware limits with every result, so the comparison can be repeated.
- Measure end to end at the entry point as well as the inner function. A faster function inside a slow request is not a fix.
- Report the measured delta against the target. A faster micro-benchmark that misses the budget is not a fix.

## PERF-QUERY — queries are bounded and planned

- Find N+1 calls and loops that issue a query or service call per item. Batch them or join them.
- Bound every result set: paginate or stream. Never load an unbounded population to filter or sort in memory. Keep pagination tie-breaks stable.
- Check each query against its real plan on representative data, following `INDEX-COVERING` in `authoring.md`. A missing index and an unusable index are both findings.
- Count queries and outbound calls per request in a test against representative data, and assert the count, so a regression to N+1 fails the build.
- Watch lazy-loaded associations and serialization that touch related rows per item. The number of queries often matters more than the shape of any one query.
- Compare the plan before and after with the same data. A plan that looks right on a small fixture may choose differently at production-sized cardinality.
- Limit external-call fan-out on the main path: count calls per request, set timeouts and bounded concurrency, and move non-critical work off the request.

## PERF-BUDGET — budgets are explicit and checked

- State latency percentile, memory, throughput and cost budgets tied to the product target. Record each as a row, with its measurement on the base and on the change:

| Budget | Target (source) | Base | Change | Evidence |
|---|---|---|---|---|
| p95 latency, search endpoint | from product requirement | measured | measured | run id, data set |

- Batch or stream large results. Cap upload and response sizes. Specify backpressure for queues (`async-jobs.md`).
- Check budgets in CI where feasible. Otherwise report `NOT RUN: <reason>` on the evidence card.
- Name an owner for each budget and the response on breach: alert, block the release, or accept the overrun with a recorded decision.

## PERF-CACHE — a cache key names every input

- The key includes every input that changes the result, including the customer scope key (`tenancy.md`). A key that omits scope is a cross-customer leak.
- Define invalidation and acceptable staleness before adding the cache. Do not cache a value whose staleness violates a business or safety rule.
- Keep the cache behind the same authorization and tenancy checks as the source it replaces.
- Bound size and TTL. Measure hit rate, and keep the cache only if it moves the budget.
- Never cache an authorization decision beyond its validity. Re-check permission where the decision is used.

## Frontend

- Core Web Vitals and bundle-size thresholds apply only when the project states or verifies them.
- Measure on a production build, not on the development server.

Prefer cheap deterministic pre-checks over expensive calls.
