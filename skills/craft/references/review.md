# Reviewing

Review the requested diff against its requirements, callers, tests, and running assumptions. Use independent review for substantial or risky changes when available. Small reversible edits need proportional verification, not a mandatory fleet or external review thread.

## Correctness before conventions

Start with the behaviors that can fail: authorization/scope, state transitions, data consistency, concurrency, external side effects, compatibility, and capability preservation. Then assess maintainability and local conventions. Use `defect-classes.md` as a prior; inspect domain-specific references when their trigger appears.

On a refactor, read `verification.md` and compare the base implementation. A removed capability together with its test can leave the suite green. Trace one real producer and consumer through changed seams; do not infer reachability from a mocked method call.

**REPRO-FIRST — establish the failing path before changing error behavior.** Reproduce with the actual input/stack when feasible, or provide a minimal failing test or concrete control-flow evidence. Distinguish root cause from symptom and state what remains unproven. Do not add catches, defaults, retries, or dependency changes merely to silence an unexplained failure.

Verify load-bearing claims against the right source: behavior against code/tests, gate results against actual output and revision, compatibility against deployed versions, external assumptions against the contract. If evidence is unavailable, report the limit; unavailable evidence alone does not establish a product defect.

**REVIEW-DISCLOSED — a disclosed deviation still needs justification.** “Verified zero consumers” answers usage, not domain meaning; “noted as a tradeoff” does not justify unrelated behavior changes. Ask whether the change belongs in scope and preserves the intended contract, then assess its rationale. Apply this equally to fluent agent reports.

For each finding, name the trigger and concrete failure, point to the smallest relevant location, explain the impact, and suggest a feasible correction. A grep hit is a lead, not a finding. Do not report a hypothetical edge case with no reachable path or demand a personal style preference contrary to the repository.

Severity follows impact: unsafe cross-customer access, lost required capability, unguarded irreversible effects, or a breaking deployed contract are blockers. Other demonstrated correctness failures should be fixed before readiness. Style and heuristic thresholds remain advisory unless repository policy makes them requirements.

## Review communication

Lead with the most important actionable result. Use concise prose or a numbered list when findings are easier to scan that way; follow the platform's required schema if one exists. Group duplicate causes rather than creating a finding for every occurrence.

Each finding includes location, failure conditions, consequence, and a concrete suggestion. Distinguish bugs from optional improvements and confidence limits. If no actionable defect is found, say so and identify material verification gaps without inventing findings.

Keep operator-sensitive/private content out of published comments. Do not post a review, resolve threads, change tracker state, or impersonate a reviewer without authorization. An automated second opinion is useful evidence, not human approval.

## Fold and re-review

Fold confirmed in-scope findings, including small related fixes when warranted. Decline a false positive with evidence; record intentional deferrals and their consequences instead of silently dropping them. Re-run checks affected by each fold.

Re-review the whole changed behavior, not only the latest patch: a fold can regress an earlier fix or widen scope. Inspect changed tests as well as product code. Keep the final description aligned with the actual implementation.

**REVIEW-ROUNDS — diagnose recurring patterns.** Stop repeating the same edit/review loop when the defect class recurs, a fix regresses, or untouched files keep producing findings. Revisit the contract, root cause, or slice. Round counts can trigger a checkpoint; they do not prove the work is correct or require abandoning a solvable task.

## Rationalizations (author and reviewer side)

Like verification, code review rationalizations often skip the actual check. Use these to spot them.

| Thought | Reality | Rule |
|---------|---------|------|
| Verified zero consumers via grep | Grep is a lead, not a finding; it answers usage but not domain meaning | `REVIEW-DISCLOSED` |
| Disclosed as a tradeoff in the PR body | Disclosure names the deviation; justification proves the design decision is sound | `REVIEW-DISCLOSED` |
| The automated reviewer approved | Automated checks are evidence of coverage, not human judgment or stakeholder approval | |
| Round 4, just merge | Recurring issues signal a contract/root-cause problem, not readiness | `REVIEW-ROUNDS` |
| Add a catch or retry so the error stops | Diagnose the failure first; a catch that masks an unknown root cause will recur | `REPRO-FIRST` |
| Only the last fold needs re-review | Folded changes can regress earlier fixes or widen scope; review the whole changed behavior | Fold and re-review |
| The agent's summary says complete | Agent reports state what was attempted; they are data, not independent verification | `REVIEW-DISCLOSED` |
| A grep hit is a finding | Grep is a search lead; inspect the context, reason, and reachability before reporting | |
| I'd write it differently | Preference is a nit at most; enforce repository policy where it exists | |
