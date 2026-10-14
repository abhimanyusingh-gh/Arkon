# Reviewing likely defect classes

This is a set of priors from historical findings and operating experience, not a current frequency ranking or a mechanical checklist. Read the requirements and reachable paths; report only demonstrated findings. Use the relevant domain reference when the diff reaches that boundary. Prioritize impact over style.

## Safety and product behavior

| Class | Concrete question | Guidance |
|---|---|---|
| Scope or permission bypass | Can an untrusted/foreign identifier reach a read, write, aggregate, export, cache or blob? Does every actor class actually authorize? | `tenancy.md`, `security.md` |
| Missing input boundary | Can arbitrary fields, destinations, payload sizes or model output become trusted domain state? | `security.md`, `llm-calls.md` |
| Content in telemetry | Can a payload, nested exception message, stored failure or metric dimension disclose sensitive data? | `observability.md` |
| Capability deleted with coverage | What did the base do that this revision no longer does? Does a literal replace a computation or a guard have no live producer? | `verification.md` |
| Harness masks a broken composition | Does the test provide context/config missing from the real app? Does the packaged artifact start and exercise the changed path? | `verification.md`, `delivery.md` |
| Lost event or repeated effect | Is work selected by the event's identity? What happens after duplicate delivery, lost response, crash or restart? | `integrations.md` |
| Unsafe job ownership | Can an expired worker still write or perform an external effect? Do claimed exclusivity and durable acceptance have real mechanisms? | `async-jobs.md` |
| Invalid state or derived value | Are transitions atomic and allowed? Do displayed and derived values share units, time selection, rounding and source precedence? | `application-design.md` |
| Unsafe migration/cutover | Are old/new versions compatible with existing rows? Is an applied migration edited? Is a prerequisite merged but undeployed? | `workflow.md`, `delivery.md` |
| Unsafe configuration | Do missing credentials or required production settings silently take defaults? Are ranges/startup checks exercised? | `authoring.md` |
| Untested upgrade runtime | Was the deployed artifact actually started? Did transitive resolution, runtime or migration behavior change? | `dependencies.md` |
| Stale or hidden UI state | Can a late response replace newer intent, a foreign view remain visible, or inactive drafts enter a saved payload? | `frontend.md` |
| Partial success represented incorrectly | Does bulk rollback undo committed items only in the UI? Does one failure hide successes or an unknown tail? | `frontend.md` |
| Hollow test evidence | Does the test fail for the intended defect? Are assertions weakened without a contract change, skips hidden, or the wrong revision tested? | `testing.md`, `verification.md` |
| Unbounded data/work | Are queries, fan-out, retries, memory, payloads and backlogs bounded? Is the actual plan appropriate at representative size? | `authoring.md`, `integrations.md`, `delivery.md` |

Scope leaks, lost required capabilities, broken deployed contracts, privacy breaches, and uncontrolled irreversible effects are blockers. Missing evidence is a limitation to investigate; do not invent a product failure from an unavailable test alone.

## Coherence and usability

| Class | Shape to investigate | Guidance |
|---|---|---|
| Duplication/layering | Divergent implementations of one policy, duplicate fetchers, provider branching in domain rules, forwarding wrappers that add nothing | `authoring.md` |
| Unwired capability versus scaffolding | Unused code implementing a required behavior; deletion based only on a usage search | `authoring.md` |
| Literal/naming drift | Competing words/units/casing for one concept, retyped finite sets, aliases obscuring dependencies | `authoring.md` |
| Design/accessibility drift | Undefined tokens, unverified supported theme, broken keyboard model, disabled semantics or focus, premature announcements | `frontend.md`, `accessibility.md` |
| Incomplete scenarios/fixtures | Required branch or relationship absent, nonisolated destructive seed/reset, selectors no longer reaching the behavior | `testing.md` |
| Dead cache/event seam | Producer invalidates/publishes a key no live consumer uses; cache identity lacks a relevant input or customer scope | `workflow.md`, `frontend.md` |
| Complexity and scope creep | A new framework/abstraction without a constraint, unrelated cleanup, mixed parsing/validation/persistence/effects, brittle narrative instead of an invariant | `authoring.md` |
| Stale documentation | Changed contract/config/operator behavior still described as before; planned capability described as shipped | `workflow.md` |

Conventions follow the actual language and repository. A raw string, native disabled attribute, inline style, or repeated field declaration is not inherently a bug. Explain the concrete drift or risk before proposing a correction. A numeric heuristic is a prompt to inspect, not a severity calculation.

Useful searches include removed tests, hardcoded replacements, exception-message access, missing scopes, repeated endpoint/key strings, skip markers, and catch-and-continue. Read the surrounding implementation and base version before turning a match into a finding.
