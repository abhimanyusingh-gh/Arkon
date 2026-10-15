# Learning from commit history

Use when adapting engineering conventions or building an application from the user's past production work. History is evidence of decisions and corrections, not a mandate to reproduce every old pattern.

## HISTORY-PROVENANCE — establish what history is available

1. Identify the requested repositories, exact author identities, local refs, date range, and shallow boundaries. A similarly named colleague is not the same author. Include all locally reachable branch refs; report when remote or older history was not fetched.
2. Deduplicate shared worktrees, duplicated clones, full commit hashes, and rebased/cherry-picked patch equivalents as separate measures. Exclude merge and stash snapshots from implementation counts, with the exclusion method stated. Neither subjects nor patch IDs establish independent incidents.
3. Read the full relevant subject/body history, then inspect the actual diffs and surrounding code for proposed patterns. Follow a correction through later changes: a new feature is not a defect, and a `fix` prefix is not proof of a production incident.
4. Link each proposed rule to repository + commit + path + observed failure or decision. Distinguish reviewer findings, self-detected rework, feature evolution, operating experience, and supplemental engineering judgment. Keep raw private source, payloads, and identity records out of distributable artifacts; publish only approved, minimized provenance metadata.

The bundled read-only inventory helper provides coverage metadata; run it from the skill directory:

```text
python3 scripts/history_inventory.py --root /path/to/workspaces --author 'precise-author-regex'
```

It does not fetch, inspect untracked files, or prove that all hosted history is available. Use `--help` for scope and optional patch-equivalence reporting. Inspect actual patches before turning its counts into guidance.

## HISTORY-CALIBRATE — keep the invariant, qualify the preference

For each candidate rule, record the failure it prevents, trigger, concrete mechanism, verification, counterexample, and confidence. Repeated independent failures across applications strengthen confidence; multiple corrections in one change sequence remain one episode.

- Preserve high-impact invariants even with few examples: authorization, privacy, loss of capability, atomic transitions. Explain their impact rather than inflating counts.
- Scope local conventions to their stack and deployment topology. A TypeScript branding pattern, one PR file budget, one framework annotation, or one scheduler's ranking policy is not a universal application requirement.
- Search deliberately for reversals. Production config may need to fail closed; an intentional product change may require updated assertions; a merged API may still be undeployed. Amend the old instruction instead of appending an opposing rule elsewhere.
- Prefer a small, decisive correction over adding another absolute. Keep the authoritative rule in one place; route to it from reviews and evidence.
- Validate on a held-out realistic task, including a different stack when claiming stack neutrality. Check observable behavior and false positives, not whether an agent repeats the rule names.

When updating this skill, keep provenance and confidence in the repository's `docs/EVIDENCE.md`; keep the reusable decision and its trigger in the runtime reference. Report the limits of the available history rather than describing local inspection as an audit of the user's entire hosted account.
