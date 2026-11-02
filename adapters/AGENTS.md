# craft

> **Experimental — untested on this platform.** Condensed from the craft skill (skills/craft/). Not extensively tested on any host other than Claude Code. Do not rely on it as a compatibility claim.

## Principles

- Name the requested outcome and the existing behavior that must survive; never delete a capability or weaken its test to reach green.
- Derive customer scope from trusted authentication and enforce authorization at the data or action boundary, including jobs, exports, caches and storage. A cross-customer leak is a blocker.
- Read the repository's instructions, callers, tests, schema and CI; search for reuse before writing new code.
- Implement one useful slice at a time; flag adjacent cleanup instead of expanding scope.
- Use native types, schemas and database constraints; brand or wrap values where a mix-up is possible. A type assertion is not input validation.
- Bound external work and retries; specify partial failure, concurrency, duplicate delivery and recovery before adding side effects.
- Run the applicable gates and report their actual output, skips and limits. An unrun check is never a pass.
- Validate external input and model output, keep sensitive content out of telemetry, and add negative tests at security boundaries.
- Keep docs current, use truthful commits, and respect approval and branch-protection rules. Never add assistant attribution.
- Severity: `blocker` must not merge; `should-fix` belongs in this change; `nit` is advisory.
- Report substantial work with the evidence card in `skills/craft/SKILL.md`. A row that says only "done" or "all tests pass" is unfilled.

## Working with agents

- If your host supports delegation, only the orchestrator delegates. It plans, reads, reviews and runs gates. It does not edit source, commit, or fix agent output itself; it sends a follow-up agent instead.
- Agents do the work themselves. Every brief says: "Do the work yourself. Do not spawn or message other agents."
- Draw the dependency graph before dispatching. Audit file overlap, send one wave per message, and cap each agent to one module and a few files.
- Use a cheap, fast tier for research, exploration, mechanical code, tests and ticket or wiki operations. Use a stronger tier for design, analysis, review and risky changes.
- Always set the tier explicitly. Omitting it silently inherits the stronger tier across the fleet.
- If your host has no delegation or no model selection, do the same work in one session and note the intended tier in the brief.

## Git and PRs

- Update a feature branch by local rebase, not the host's "update branch" button. Fetch, rebase, rerun the affected gates, and push with `--force-with-lease`. Never force-push a protected branch.
- Branch prefixes are lowercase. A commit subject follows the repository's required format exactly. Renaming a PR's head branch closes the PR.
- Push only finished commits. No WIP or placeholder commit reaches the remote; squash any local WIP before the PR.
- Before any push, run the formatter check, the linter and the repository's commit linter, and report each as its own row with its real output line.
- A PR adds no static-analysis vulnerabilities and no open security hotspots.
- Commits and PR bodies carry no assistant attribution, generated-by footer or co-author trailer. Grep the commit messages and PR body before pushing. A project instruction may ask for one; a host default does not.
- Keep the PR body short. Name each entity the change touches (tenant, service, route, repository) and where it maps. No method-name lists or file counts.
- Merge only when authorized, required checks are satisfied, and findings are resolved or explicitly accepted under repository policy.

## Verification

- A gate is proven by its output. Record the command, the revision tested, the exit status, the counts and the output. A timeout, partial output or still-running process is pending, not green.
- A gate that cannot run is reported as `NOT RUN: <reason>`. Reproduce an agent's "cannot run" claim once before accepting it.
- On a refactor, diff against the base for what was lost, not only what was added: domain terms that vanished, removed tests, a literal where a variable used to be, and guards no input can reach.
- Deleting, skipping or weakening coverage to hide a regression is a blocker. A replacement test must name the invariant it protects; a retired capability must name the intentional requirement change.
- After any rebase, conflict resolution or cherry-pick, compare the test declaration count and the test-file line counts with the base. A drop needs a named deletion or a restored test.
- Focused test runs are for iteration. Final validation runs the full applicable suites.

## Stack notes

Load the note that matches the repository, then read the matching profile in `skills/craft/references/stacks/`.

**JVM / Maven service.** Applies to a root `pom.xml` with `src/main/java` or `src/main/kotlin`. Run the format check, compile every touched module, run the full unit suite, then the integration suite, and confirm the integration binding ran tests. Pin the JDK explicitly.

**React / TypeScript UI.** Applies when `package.json` lists React and a `tsconfig.json` exists. Run typecheck, lint, the full unit suite and a production build; a development server is not a build. Do not use inline `style` props.

**Apex / LWC.** Applies with `sfdx-project.json`, `*.cls` files or `lwc/` bundles. No SOQL, DML or callouts inside loops; test a batch of 200 or more records. Deleting a field deletes its data, so a removal is a separate reviewed change.

**Config and deploy repositories.** Applies to Helm charts, per-environment `values*.yaml` or Flux manifests. Name the target environment and the owning service, paste the rendered diff, never commit plaintext secrets, and state the exact revert.

**SQL migrations.** Applies to `db/migration` directories and versioned `V*__*.sql` files. Test on a disposable database built from the prior deployed schema with representative rows. Never edit an applied versioned migration; add a corrective one. Every new table carries the scope key.

**LLM-backed features.** Applies to model SDK dependencies, prompt templates or model-call wrappers. Enforce invariants in code, not only in the prompt. Log identifiers, call type, token counts and error codes, never personal or clinical text. A prompt or model version change ships with an evaluation run.

## Full skill

The full skill, with every boundary reference and the evidence card, is in [`skills/craft/SKILL.md`](../skills/craft/SKILL.md). Read the reference that matches the boundary you are touching. This file is a draft condensation and is not the skill.
