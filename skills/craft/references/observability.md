# Observability and telemetry privacy

Covers logs, metric tags, stored failure reasons, trace attributes, and error response bodies. These are one rule because they are one leak: record content reaching a sink that outlives the request. Apply it to any system holding personal or health data; elsewhere it is good hygiene, not a gate.

The project's own logging guidelines (levels, schema, retention, trace ids) still apply. This reference adds mechanism, and tightens one thing: what an exception is allowed to carry.

## Identifiers and content

| Allowed | Not allowed |
|---|---|
| Opaque ids (record id, document id), attempt number, outcome, duration, counts, lengths, enum values, flag names, exception class names, a code location | Names, dates of birth, measurements, diagnoses, medications, document text, model output, upstream free text, exception messages on data-bearing paths, tokens and keys |

A pseudonymous id (a person's user id) is still personal data under privacy law. Log it only where the id is what you need to debug, and keep it out of metric tags.

## Rules

**LOG-FIELDS — structured key/value fields, not formatted messages.** The message is static text; the variable parts are named fields.

- Field keys are constants in one place (`ENUM-CONST`), one key per concept (`NAME-TAXONOMY`). A key typed twice becomes two columns in the log store.
- A logging helper takes alternating key and value pairs, rejects an odd count or a non-string key at the call, omits null values, and restores any thread-local context in `finally` so fields never leak into the next line on that thread.
- Correlation or request id is a field on every line in a unit of work (`LLM-CORRELATE`).
- Level policy: state change and unit completion at info, idle repetition at debug. A poll that fires every few minutes logs info only when something changed.
- Never format a value into the message string. It defeats aggregation and is how content gets in.

**LOG-FAILURE — describe a failure by class and place, never by message or trace.** Blocker when the exception can carry record content (parse, serialisation, ORM, HTTP-client and driver exceptions all can echo their input); otherwise should-fix.

```text
describeFailure(e) = class(e) + " root=" + class(rootCause(e)) + " at " + topFrame(rootCause(e))
```

- Log fields, stored failure reasons and response bodies take `describeFailure`, truncated to a fixed length. Not the message, not the stack trace, not the exception object.
- One helper, reused. A second copy is `REUSE-*`.
- A wrapping exception does not splice in its cause's message: `new X("failed: " + cause.message, cause)` moves the content into a message some later catch will log.
- HTTP error bodies are fixed strings per failure class. Never the exception message.
- Metric tags never take exception text.
- The cost is a thinner stack for debugging. Pay it with a correlation id, the root class, and the code location, and keep the full trace for paths that provably hold no record content.

**LOG-LENGTH — free text from a model or an upstream system is logged as a length.** A stable id plus a length is enough to find the record and the symptom.

- Log a value raw only **after** it has been validated against a known set. An id the model returned that matches a sent id is safe to log; one that does not is logged as `idLength`.
- No upstream or model value as a metric tag. Tags are enum values only (`JOB-OUTCOME`).
- If a field is a controlled list today but could become free text, say so where it is logged.

**LOG-SENTINEL — every place that logs or stores a failure has a test that tries to leak.**

- The test throws an exception whose message carries a realistic content sentinel (a name plus a lab value), and again with the sentinel in a nested cause.
- It asserts on **all** captured text: messages and field values, not only the message. Also on the stored failure reason.
- Success paths get the inverse: a usage or outcome line contains only its allowed fields and never the result.
- The capture helper attaches and detaches cleanly and records field values, so a leak through a field fails the test.
- One sentinel test per catch site, not one per class. The sentinel is the regression test for the next person who adds the message "just for debugging".

## Reviewer checklist

1. Grep the diff for message accessors (`getMessage`, `getLocalizedMessage`), `printStackTrace`, and a throwable passed as a log argument. Each hit on a data-bearing path is a finding.
2. Do stored failure reasons and error response bodies use the helper or a fixed string?
3. Are metric tags enum values, with no id or upstream value?
4. Is each unvalidated external or model string logged as a length?
5. Does each new catch site have a sentinel test over all captured text?
6. Are log keys constants, and is the message static?
7. Is the correlation id a field on the line?

Common misses: a wrapped exception message that a later catch logs; an error body echoing the exception message; a metric tag from an upstream field; an assertion on the message only; a "temporary" debug line that logs the payload.
