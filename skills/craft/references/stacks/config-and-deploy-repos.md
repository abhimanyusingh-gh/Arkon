# Config and deploy repositories

Helm charts, GitOps manifests and environment configuration. Load with the generic rules in the skill. Changes here alter running systems without touching application code, so the checks below come before the diff review.

## Match signals

- **Requires:** a Helm `Chart.yaml`, or `kustomization.yaml`, `HelmRelease` or `GitRepository` manifests in per-environment directories (`environments/`, `overlays/`, `clusters/`).
- Supporting: `values*.yaml` and a `templates/` directory (Helm), a SOPS `sops:` block, sealed-secret resources, or a `.sops.yaml` rule file.

## Gates

1. Target environment: apply [ENV-TARGET-CONFIRM](../project-binding.md). Here the target is the cluster and namespace the owning service runs in, not the directory name.
2. Rendered diff: render the chart or overlay for each touched environment with the repository's render step, and paste the diff of the rendered output. The source diff alone does not show what changes.
3. Schema validation: run the manifest validator the repository uses on the rendered output and paste the result.
4. Secrets: confirm no plaintext secret value enters the diff, by the repository's encryption tool or a search for secret keys carrying literal values. A removed secret is named in the PR body.
5. Revert path: the PR body states the exact revert (the commit to revert, or the previous values) and whether reverting is safe once the new config has reconciled.
6. Cross-repo ordering: apply [DELIVERY-CROSS-REPO](../delivery.md). Verify the consuming service starts with the new config in a lower environment before merge.

## Pitfalls

- Wrong environment: prefer a revert when the revert is safe after reconciliation; otherwise fix forward in a separate reviewed change, stating why. A forward patch to the wrong environment leaves two changes to unwind.
- One environment per change unless the PR says otherwise. A shared base file changes every environment that inherits it, so check inheritance in the rendered output for each one.
- Flipping a feature toggle across environments is its own reviewed change. It does not ride along with a values tidy-up.
- Shared-environment trials: apply [ENV-SHARED-TRIAL](../project-binding.md). Reproduce the setting in a lower environment first, then change the shared one in a reviewed PR.
- A required variable that is missing should fail startup. Do not add a silent chart default that hides the gap; a default that changes behaviour is a feature toggle in disguise.
- Plaintext secrets are never committed, including to development environments. A secret that was committed is rotated, not only deleted from the history.
- A changed image tag or digest is a rollout. Treat it with the readiness checks in [delivery](../delivery.md).
- Confirm which configuration profile the deployed runtime activates. A property the runtime never reads is dead config, and a passing rendered diff does not show that.
- Migration-tool settings that clean, repair or skip validation are never enabled on a shared environment through config. See [sql migrations](sql-migrations.md).
- Chart and image upgrades follow [dependencies](../dependencies.md): pin the version, and do not bump a major version in a configuration PR.

## Pointers

- [delivery](../delivery.md): readiness, rollout and recovery
- [workflow](../workflow.md): gates, PR scope and commit truth
- [tenancy](../tenancy.md): per-tenant settings and scope keys in config
- [dependencies](../dependencies.md): chart and image version changes
- [security](../security.md): secret boundaries and configuration that fails safely
