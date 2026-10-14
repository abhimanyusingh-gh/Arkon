# Calls to an external model

Provider-neutral: the rules hold for any hosted model behind any client library. They apply wherever a service sends data to a model and acts on what comes back.

## Rules

**LLM-CORRELATE — every model call carries a correlation id, and it reaches the logs.**

- Every port method that reaches the model takes a correlation id and hands it to the client request. A port without one is a defect.
- Build it in one place, at the worker that owns the unit of work, from stable ids: `unitId:attempt` (or `unitId:stage:attempt`). The same id is reused for every call within one attempt; the call type tells them apart.
- It contains no secret, no claim or fencing token, and no record content (`LOG-FAILURE`). Test the format.
- Synchronous request paths mint one at the entry point. A null id means the call is invisible in the provider's logs and in yours.
- It appears on the usage line and on every failure line for that attempt (`LOG-FIELDS`).

**LLM-USAGE — log token usage on every call, with an explicit availability flag.**

- One helper, one record per call: call type, correlation id, `usageAvailable` true or false, prompt, completion and total tokens, and derived reasoning tokens where the library only reports a total.
- Never write a silent zero when usage is missing. The flag says "not reported".
- The record carries usage fields only. Never the prompt, never the result.
- Logging is the floor. When spend is budgeted, add a counter by call type and a cost alert. Check what the client library already meters (latency and sizes are common; tokens often are not) before assuming it is covered. Nit, should-fix when spend is budgeted.

**LLM-RETRY — one shared retry policy, bounded at two levels, with the multiplication stated.**

- One policy object used by every call: a small retry count, exponential backoff with a cap, and an explicit list of retryable failures (rate limit, timeout, malformed output, transient I/O). Validation failures do not retry. Counts and delays are config (`CONFIG-DAY`).
- Every call has an explicit timeout sized to its payload. A document-sized call and a text-only call do not share one.
- The job around the calls has its own budget (attempts per window, windows). The worst-case calls per unit is the product of the two levels and the number of calls per attempt. State that number in the PR. Example: 5 calls per attempt x 3 attempts x 3 windows = 45 per unit.
- A late-stage failure that re-runs earlier stages multiplies cost again. If stages are expensive, persist a stage result or say why not.
- Do not spend a call on a unit that may already be finished upstream unless a cheap check is not available; if it is not, record that as an accepted cost.

**LLM-FAILSAFE — model output is untrusted input, and failure is a defined outcome.** Blocker if unvalidated output drives a clinical, financial or irreversible action.

- Strip wrappers (code fences, prose), then parse into a typed shape. A parse failure is an error with a fixed message (`LOG-FAILURE`), never a guess.
- Validate every returned id against the set you sent. Unknown id: drop and log by length (`LOG-LENGTH`). Unexpected enum value: drop, never default to a favourable one.
- An empty or null result is a defined value, not an exception and not a success.
- Never persist a partial result after a parse failure.
- Failure feeds the job's outcome (retry, defer, fail), not a swallow, and exhaustion raises an alert (`JOB-OUTCOME`).
- Put the feature behind a default-off flag whose lookup failure means off (`JOB-GATE-ORDER`).

**LLM-PROMPT — prompts are versioned resources built from minimised, structured input.**

- Prompt text lives in a resource file loaded at startup, not concatenated inline. A prompt change is a diff to a file.
- Build user content from an explicit field list, never "the whole record". Send the minimum the task needs; names and identifiers the model does not need stay out.
- State the output shape in the prompt and keep it in step with the parse type. A prompt change and a parse change ship together.
- A prompt change ships with a parse test against a realistic output, including the awkward ones (fenced, trailing prose, missing field).
- The call type names the call in metrics and logs (`LLM-USAGE`).

## Reviewer checklist

1. Does each new port method take a correlation id, and is it built in one place?
2. Is there a usage record per call with an availability flag, and no content in it?
3. Is there one shared retry policy, explicit timeouts, and a stated worst-case call count?
4. Is output parsed to a typed shape and validated against what was sent?
5. What happens on empty, malformed, or partially valid output? Is it covered by a test?
6. Is the feature flagged off by default?
7. Does the prompt come from a resource, built from an explicit field list?
8. Does a prompt change come with a parse test?

Common misses: a null correlation id on the synchronous path; an unbounded product of retry levels; trusting an id the model returned; defaulting an unknown enum to a favourable value; logging the model response "to debug".
