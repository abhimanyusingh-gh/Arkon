# Observability and telemetry privacy

Covers logs, metric tags, stored failure reasons, trace attributes, and error response bodies. Keep secrets out of these sinks in every system. Apply the stricter content rules to paths carrying personal, health, financial, or confidential data, according to the project's access and retention policy.

The project's own logging guidelines (levels, schema, retention, trace ids) still apply. This reference adds mechanism, and tightens one thing: what an exception is allowed to carry.

## Identifiers and content

| Allowed | Not allowed |
|---|---|
| Necessary opaque ids, attempt number, safe outcome/error codes, duration, counts, lengths, non-sensitive enum values, flag names, exception class names, a code location | Names, dates of birth, measurements, diagnoses, medications, document text, model output, upstream free text, exception messages on data-bearing paths, tokens and keys |

A pseudonymous id (a person's user id) is still personal data under privacy law. Log it only where the id is needed to debug and permitted by the sink's policy; keep it out of metric tags. Membership in a known set does not make a diagnosis, email address, or patient identifier safe to log.

## Rules

**LOG-FIELDS — structured key/value fields, not formatted messages.** The message is static text; the variable parts are named fields.

- Reuse the project's logging API and field schema: stable keys, one key per concept (`NAME-TAXONOMY`). Prefer typed fields or the framework's structured builders; do not build a custom logger merely to satisfy this reference.
- If a shared adapter is necessary, validate its field shape and restore scoped context in `finally`. Propagate context across async boundaries with the framework's supported mechanism; thread-local context alone does not follow coroutines or executor tasks. Test concurrent units for context isolation.
- Correlation or request id is a field on every line in a unit of work (`LLM-CORRELATE`).
- Level policy: state change and unit completion at info, idle repetition at debug. A poll that fires every few minutes logs info only when something changed.
- Never format a value into the message string. It defeats aggregation and is how content gets in.

**LOG-FAILURE — retain useful diagnostics without copying sensitive exception content.** Passing a raw exception/message to a broadly accessible sink is a blocker when it can carry protected content; parse, serialisation, ORM, HTTP-client and driver exceptions can all echo input. Public error bodies follow a stable error contract and never expose internal messages or stacks.

```text
safeFailure(e) = { errorCode, exceptionClass, rootCauseClass, safeCodeLocation, correlationId }
```

- Logs and stored failure reasons use this safe structure or a shared bounded description. Include an operation/stage and safe upstream status code when they help distinguish causes. Public responses carry the agreed error code and request id, not the internal descriptor.
- Reuse one sanitization path. Inspect nested causes, suppressed exceptions, and structured field values; bound traversal and handle a missing stack or cyclic cause chain. A second copy is `REUSE-*`.
- A wrapping exception does not splice in its cause's message: `new X("failed: " + cause.message, cause)` moves the content into a message some later catch will log.
- HTTP error bodies map failures to safe, stable error codes/messages. Keep internal class names and code locations in diagnostics.
- Metric tags never take exception text.
- Preserve sanitized stack frames when needed: class, method, file and line without exception messages or payloads. Full exception rendering can include cause/suppressed messages even when the top-level message is safe. Raw traces are allowed only where their content and sink policy have been verified safe; use established redaction support rather than erasing every trace.

**LOG-LENGTH — diagnose protected external content through safe metadata.** Prefer a necessary opaque id, content length and error code over copying free text from a model or upstream system.

- Validation against a known set proves provenance, not privacy. A returned id must both match a sent id and meet the opaque-id/necessity policy before logging; otherwise log its length. Controlled diagnosis values remain sensitive.
- Metric dimensions are bounded, reviewed sets such as outcome, operation and provider error category (`JOB-OUTCOME`), never record ids, raw upstream/model strings or exception text. Preserve established safe dimensions such as service/version; finite cardinality alone is not a privacy check.
- If a field is a controlled list today but could become free text, say so where it is logged.

**LOG-SENTINEL — sensitive failure paths have a test that tries to leak.** Cover each distinct catch/sanitization path, using shared parameterized tests where behavior is shared.

- The test throws an exception whose message carries a realistic content sentinel (a name plus a lab value), and again with the sentinel in a nested cause.
- It asserts on **all** captured text: messages and field values, not only the message. Also on stored failure reasons and returned error bodies where applicable; include nested and suppressed exceptions when the runtime supports them.
- Success paths get the inverse: a usage or outcome line contains only its allowed fields and never the result.
- The capture helper attaches and detaches cleanly and records field values, so a leak through a field fails the test.
- Assert the safe code, operation and correlation remain available. Privacy tests must also preserve enough evidence to diagnose the failure. Add a case when a catch site has a different serializer or sink; do not repeat identical helper tests at every wrapper.

## Reviewer checklist

1. Search the diff for message accessors (`getMessage`, `getLocalizedMessage`), `printStackTrace`, and throwable log arguments. On sensitive paths, verify the sink receives sanitized fields rather than raw content; a matched accessor alone is not proof of a leak.
2. Are stored failures sanitized and public errors stable, with useful internal diagnostics retained?
3. Are metric dimensions bounded and non-sensitive, with no record id or raw upstream value?
4. Is each unvalidated external or model string logged as a length?
5. Do distinct sensitive failure paths have sentinel coverage over all captured text?
6. Does logging reuse the established field schema, with a static message?
7. Does correlation survive async execution without crossing between units?

Common misses: a wrapped exception message that a later catch logs; an error body echoing the exception message; a metric tag from an upstream field; an assertion on the message only; a "temporary" debug line that logs the payload.
