# Calls to an external model

Provider-neutral: the rules hold for any hosted model behind any client library. They apply wherever a service sends data to a model and acts on what comes back.

## Rules

**LLM-CORRELATE — every model call can be traced to its unit of work.**

- Propagate the existing trace/correlation context through the model adapter, including async work. An explicit port parameter is one option; do not add redundant parameters where framework context already reaches the call.
- Build or inherit correlation at the unit's entry point. Use one attempt correlation plus a stage/call sequence to distinguish calls and retries. Opaque ids such as `unitId:stage:attempt` are acceptable only under the identifier policy in `observability.md`.
- It contains no secret, no claim or fencing token, and no record content (`LOG-FAILURE`). Test the format.
- Send correlation metadata only where the provider supports it and the data policy permits it. Capture a provider request id when available. Providers without custom correlation still get local trace coverage; do not invent a request field the SDK does not support.
- It appears on the usage line and on every failure line for that attempt (`LOG-FIELDS`).

**LLM-USAGE — record reported usage with its actual availability.**

- One helper, one usage record per provider response: call type, correlation id, provider/model, `usageAvailable`, and reported input, output and total token counts. Preserve per-field absence; a provider can report a total without its components.
- Reasoning/cached token counts are optional provider-reported breakdowns. Derive them only when a documented accounting relationship and all required components exist; a total alone cannot identify reasoning tokens. Do not add reasoning tokens to output tokens if the provider already includes them there.
- Missing fields are absent/null, never invented zeroes. Zero is a reported value. On timeouts or interrupted streams, usage/spend may be unknown; record that outcome rather than claiming the call cost nothing.
- The record carries usage fields only. Never the prompt, never the result.
- When spend is budgeted, meter by bounded call type/model dimensions and reconcile unknown calls where possible. Price estimates identify their rate version and token categories; an alert detects spend but does not enforce a budget. Use a configured per-unit/run budget or admission control when overspend would violate a requirement. Check existing client metering before duplicating it.

**LLM-RETRY — retries are coordinated, bounded, and costed at every level.**

- Reuse a shared classification/backoff policy, with per-call budgets where workloads differ. Use capped exponential backoff with jitter, and respect provider retry delays within the overall deadline. Retry transient failures deliberately; authentication, invalid input and permanent quota/configuration errors fail without repeated calls. Malformed output can receive a bounded retry if the outcome contract permits it.
- Audit SDK, adapter, queue and job retries together. Disable redundant retry layers or state the bound using **total attempts, including the initial attempt**: `stages × adapter attempts × SDK attempts × job attempts per window × windows`. Example: 5 stages × 2 adapter attempts × 3 SDK attempts × 3 job attempts × 3 windows = 270 provider requests per unit. Variable stages use a sum of their bounds.
- Bound both an individual request and the overall stage/run deadline, including backoff, and propagate cancellation. Payloads with different latency requirements may need different timeout budgets; derive them from measured/provider limits rather than forcing every call type to differ.
- A late-stage failure can repeat expensive earlier stages. Persist reusable stage results keyed by input/prompt/model version when justified, or explain the accepted replay cost. Retries of tool actions use external-effect idempotency (`JOB-EFFECT`); a timeout does not prove the effect failed.
- Do not spend a call on a unit that may already be finished upstream unless a cheap check is not available; if it is not, record that as an accepted cost.

**LLM-FAILSAFE — model output is untrusted input, and failure is a defined outcome.** Blocker if unvalidated output drives a clinical, financial or irreversible action. Treat document/user content as data rather than instructions; model output never bypasses authorization, scope checks, or permitted-tool boundaries. See `INJECTION-BOUNDARY` in `security.md` for policies on untrusted input and outbound channels.

- Prefer provider schema support where available, then validate locally into a typed shape. Remove only wrappers explicitly allowed by the contract; guessing a JSON substring from arbitrary prose can accept the wrong result. A parse failure has a safe error code (`LOG-FAILURE`).
- Validate returned ids against the sent/authorized set, enums, ranges and required cross-field invariants. Unknown id or enum: reject the affected result according to the contract and log safely (`LOG-LENGTH`), never default to a favourable value. Partial acceptance must be explicitly allowed; silently dropping invalid entries must not turn a consequential incomplete result into success.
- Empty, null, refusal and truncated output each have a defined outcome. Whether empty is valid no-result or a failure depends on the task; do not confuse it with successful processing.
- Never persist a partial result after a parse failure.
- Failure feeds the caller's outcome (retry, defer, fail), not a swallow; background jobs use `JOB-OUTCOME`. Apply human confirmation or review when the product requires it for consequential actions.
- New optional/costly automation uses a default-off kill switch whose lookup failure means off (`JOB-GATE-ORDER`). Preserve the operating policy of existing essential functionality.

**LLM-PROMPT — prompts and output contracts are versioned and tested.**

- Reuse versioned prompt resources for substantial templates; smaller prompts may live in the project's existing versioned code/config. Record prompt/model/schema versions without logging content so a result can be traced to its producing contract.
- Build user content from an explicit field list, never "the whole record". Send the minimum the task needs; names and identifiers the model does not need stay out.
- State the output shape and keep it consistent with the parse type. A shape change updates prompt/schema, parser and fixtures together; a wording change need not change the parser.
- Test representative task outcomes as well as parsing: correct domain decisions, invalid/foreign ids, missing fields, refusal, truncated and allowed wrapped output. Use a small versioned evaluation set for consequential prompt/model changes; parser acceptance alone is not evidence of task quality. Live-provider evaluation depends on available credentials, cost and the task's authorization.
- The call type names the call in metrics and logs (`LLM-USAGE`).

## Reviewer checklist

1. Does trace context reach each call, with provider request ids captured where supported?
2. Is reported usage distinguished from missing fields and uncertain spend, with no content logged?
3. Are SDK and job retries included in the cost bound, with jitter, deadlines and cancellation?
4. Is output parsed to a typed shape and validated against what was sent?
5. What happens on empty, malformed, or partially valid output? Is it covered by a test?
6. Does new automation have its required kill switch and spend controls?
7. Is the prompt versioned, built from an explicit minimized field list?
8. Do prompt/model changes validate task quality as well as parsing?

Common misses: missing trace context on synchronous or async paths; SDK retries omitted from the bound; invented reasoning-token counts; replaying an ambiguous tool effect; trusting a returned id; logging the model response "to debug".
