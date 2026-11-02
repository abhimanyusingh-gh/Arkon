# Reviewing likely defect classes

This is a set of priors from historical findings and operating experience, not a current frequency ranking or a mechanical checklist. Read the requirements and reachable paths; report only demonstrated findings. Use the relevant domain reference when the diff reaches that boundary. Prioritize impact over style.

## Safety and product behavior

| Class | Concrete question | Guidance |
|---|---|---|
| Scope or permission bypass | Can an untrusted/foreign identifier reach a read, write, aggregate, export, cache or blob? Does every actor class actually authorize? | `tenancy.md`, `security.md` |
| Missing input boundary | Can arbitrary fields, destinations, payload sizes or model output become trusted domain state? | `security.md`, `llm-calls.md` |
| Private data + untrusted content + outbound effect | Can a session access customer data, ingest external content and perform irreversible actions? What prevents instruction injection? | `security.md` |
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
| Spec divergence or unrequested behavior | Does every stated requirement have an implementing path, and does the diff add behavior nobody requested? | `review.md` REVIEW-SPEC |

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

## Rules for classes the tables do not name

**LLM-INVARIANT-CODE — enforce model-output invariants in code, not only in the prompt.** A stored verdict must not contradict its inputs, and thresholds and counts are checked by a validator or sanitiser after parsing. Prompt wording is advisory; the code path is the control. Keep control content (verdict labels, scoring markers, routing tokens) out of prompts where the model can echo it into output. When the same output class has been fixed more than once, move the invariant into code instead of revising the prompt again. Extends `LLM-FAILSAFE` in `llm-calls.md`.

**PICK-DUPLICATE — one change lives on one branch.** Before opening or pushing, check for the same change replayed on several branches (`git cherry` against the base, or patch-ids). Consolidate onto one branch rather than carrying duplicates. A duplicate cherry-pick is a review finding.

**CONTRACT-LIVE — a dependency on another service is verified on that service's main branch.** When a change calls another service's endpoint or reads its schema, confirm on that service's main branch that the endpoint and fields still exist before merge. Record the dependency and the verified revision in the PR body.

**LIB-NATIVE-FIRST — check the library's own API before writing custom code or CSS.** Read the library's type definitions or documented options for a native feature first. Port an approved mockup verbatim: copy its paths, formulas and markup rather than paraphrasing them. A paraphrased port that changes behaviour is a blocker.

**DOC-CHECK — re-read a published document after writing it.** Read wiki pages and runbooks back after the write. Remove placeholder text. Tick template checkboxes only for items actually done. Link tickets and PRs instead of printing raw commit hashes.
