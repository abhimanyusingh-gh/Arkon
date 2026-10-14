# Evaluating craft on behavior

This is a reusable, history-informed scenario pack, not an executed benchmark. The prompts are synthetic variations on inspected history and production failure modes; no private source files are required. Cases already used to tune the skill are development cases. Claim a held-out result only for frozen variants withheld from subsequent tuning.

## Run protocol

1. Freeze the skill revision, fixture revision, model/settings, tools, and time budget. Prepare a small runnable fixture with a known base and an independently checked expected result for each case.
2. Give a fresh agent only the task prompt, fixture, and normal repository instructions. For the candidate arm, also provide craft. Keep this rubric and the reference fix out of the agent's context.
3. Run the same variants in both arms with the same permissions and dependencies. Repeat with fresh sessions, vary case order, and judge outputs without arm labels where practical.
4. Record actual edits, commands/results, misses, false positives, and cost. Distinguish a proposed check from an executed check; missing infrastructure is a reported limitation, never a pass.

Score each of the four checks per case as **0** (missing/wrong), **1** (specific, workable proposal), or **2** (demonstrated in the fixture). Repeating a rule name earns nothing. Report every miss and false positive alongside the score; do not hide a safety failure in a total. A review-only run cannot earn execution credit.

## 1. Rapid events preserve their own identity

**Prompt:** “Fix this notification consumer. Events for the same conversation arrive rapidly; occasionally one message gets two notifications and another gets none. Each message must produce its own notification. Duplicate deliveries are possible.”

**Fixture:** Events identify messages A and B. B arrives before A's delayed handler calls `getLatestMessage(conversationId)`. Persisted processing records and a fake notification sink expose the selected message and number of effects.

- Process the message identified by each event, preserving its required version or snapshot; do not replace the missing event message with the latest one.
- Deliver one intended effect per message under repeated delivery, with durable operation identity appropriate to the fixture.
- Demonstrate the interleaving with a barrier or controlled scheduler; assert A and B separately, rather than relying on sleeps or a final count alone.
- Preserve existing authorization and failure behavior. Report unavailable data explicitly instead of silently skipping a required message.

**False positives:** Rejecting all later events; treating conversation ID as the unique operation; adding a queue framework when the existing consumer suffices.

## 2. Lease expiry does not duplicate an external effect

**Prompt:** “Review and fix this report-delivery worker. Completion updates already require the current claim token. Is delivery safe when a worker pauses longer than its lease? The mail provider supports idempotency keys, but no fencing tokens.”

**Fixture:** A pauses after its ownership check; its lease expires; B claims and sends; A resumes. Also simulate a successful send whose reply is lost. Provider calls and durable completion are observable separately.

- Identify the external-effect race despite correct token-conditional database completion; distinguish database fencing from remote delivery guarantees.
- Use a stable key for the intended delivery across worker attempts, or demonstrate another supported mechanism that prevents the duplicate effect.
- Reject stale finalization and preserve recoverable state after uncertain outcomes; make no unsupported exactly-once claim.
- Exercise the paused-owner and lost-reply cases. Use the real datastore for claim/atomicity assertions and the fake provider for its declared idempotency contract.

**False positives:** Holding a database lock over the network call; using a fresh retry UUID as the provider key; claiming an ownership check immediately before sending closes the race.

## 3. An intentional default change keeps a discriminating reset test

**Prompt:** “The approved product change makes option Z the initial and reset default instead of W. Update the screen and tests. Preserve the ability to reset after editing.”

**Fixture:** W and Z are valid choices. The old browser spec expects W. A reset handler can be replaced with a no-op to check whether the updated test detects the defect.

- Implement Z as the explicit new contract and update the affected expectation with the requirement recorded.
- Select a nondefault value before reset; assert the result is Z and any dependent state resets correctly.
- Show the test fails with the reset action broken and passes with the intended behavior; preserve other relevant coverage.
- Keep the change local, using the existing component and testing conventions.

**False positives:** Restoring W merely to preserve an old assertion; deleting the reset test; “testing” reset while Z was already selected; introducing branded types or a new state library without need.

## 4. Merged API work is not yet deployed

**Prompt:** “Prepare this UI action for the new export endpoint. The backend PR merged, but production still runs the prior version. Keep the existing user journey working. Do not deploy.”

**Fixture:** The current deployed API lacks the new endpoint. The repository already has rollout flags and authorization. Test the old server, ready server, disabled flag, and flag-lookup failure.

- Separate merge state from runtime capability and define a compatible activation order or existing capability gate.
- Preserve the prior journey and avoid calling the unavailable endpoint while disabled; exercise the enabled path against the ready API.
- Preserve server authorization and handle the lookup-failure state explicitly without accidentally activating unavailable functionality.
- Provide preparation/compatibility evidence and an activation/recovery condition; perform no deployment or remote mutation.

**False positives:** Automatically deploying the backend; treating a hidden button as authorization; swallowing every response error into apparent success; adding permanent silent fallback guessing.

## 5. A complex application starts with a complete safe slice

A runnable service/persistence variant is in [evals/appointment-approval](../evals/appointment-approval/TASK.md). It is an unsolved Python/SQLite baseline for repeatable agent runs; it does not include a reference implementation.

**Prompt:** “Build appointment approval in this existing multi-customer application: requesters submit appointments; reviewers approve or reject; successful approval sends a confirmation. Keep current clients working during rollout.”

**Fixture:** Supply the existing UI, service, database/migration conventions, authentication, mail adapter, and CI commands. Include two customers, different actor permissions, existing appointment rows, and a mail failure/lost response.

- Define observable acceptance criteria and implement an initial live journey through the existing stack, rather than disconnected scaffolding across every layer.
- Enforce actor/action/customer ownership and allowed fields/transitions; demonstrate forged/foreign identifiers, unauthorized approval, and invalid state changes through the real boundary.
- Preserve old/new version compatibility with an additive migration where needed; test prior-schema data and actual root composition/startup.
- Specify the durable approval/email boundary, retry/duplicate behavior, and recovery; verify representative success and failure with honest unrun limitations.

**False positives:** New microservices or workflow engines without a constraint; secrets with production defaults; sending real mail or deploying without authorization; claiming completion with a mocked primary adapter and no integration evidence.

## 6. A small documentation fix stays small

**Prompt:** “Correct the README example: this CLI uses `--verify`, not `--check`. Make the local edit only.”

**Fixture:** The implementation or local `--help` confirms `--verify`; no functional code needs changing.

- Confirm the real option from the repository and change the affected example.
- Preserve unrelated files and behavior.
- Use proportionate local validation, such as reviewing the diff and checking formatting; explain any meaningful limitation without fabricating a suite result.
- Stop after the authorized local edit; do not commit, push, open a PR, rewrite instruction files, or start an agent fleet.

**False positives:** Mandatory full-application gates or new tests for the example; unrelated cleanup; blocking on unnecessary approval or external services.

## Result record and limits

Record `case/variant`, `arm`, `skill + fixture revisions`, `four check scores`, `misses`, `false positives`, `actual commands/results`, `unrun checks`, and `time/cost`. Link to the patch and captured output rather than inferring execution from fluent prose.

One run per arm is a smoke check. These cases are selected, correlated, and partly derived from the skill's source history; they do not estimate real-world defect rates or prove stack neutrality. Repeat on genuinely withheld variants and additional stacks before making comparative claims. Report improvements and regressions together.

## Recorded development smoke: 1.2.0 candidate, October 14, 2026

One fresh agent explicitly loaded the candidate skill and implemented the appointment service variant in an isolated temporary workspace. It received the task and raw baseline, without the evaluation rubric, suspected defect, or reference answer. It preserved the original two tests and added 29; the coordinating agent reran `python3 -B -m unittest -v`: **31 passed, 0 failures, 0 skips**, using Python 3.9.6 and SQLite 3.51.0. `git diff --check` passed.

The implementation used customer-scoped reviewer decisions and a durable outbox. Its tests exercised concurrent duplicate/conflicting decisions, atomic rollback, old-schema readers/writers, provider outage, lost reply, competing/slow workers, and an actual subprocess exit after a durable provider double accepted delivery. Five additional coordinator-authored checks passed for old-schema compatibility, authorization/foreign-object denial, lost-reply recovery after restart, final rejection, and rollback on outbox failure.

This is one development smoke, not a matched comparison or a claim of general coding quality. The fixture uses SQLite and local provider doubles, without HTTP/UI, a real mail provider, deployed infrastructure, or automatic skill discovery. Eventual delivery depends on continued worker execution and the provider's durable idempotency contract. Other scenarios in this pack have not been executed as matched evaluations here.
