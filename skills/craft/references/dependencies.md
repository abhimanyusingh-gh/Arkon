# Dependencies, CVEs and upgrades

Version management, CVE remediation, and test infrastructure compatibility. Derive package-manager, runtime, and deployment checks from this repo; the examples below are not universal commands.

## DEP-BOOT

After a runtime, framework, or BOM upgrade, build and launch the actual deployable artifact under representative configuration. Verify readiness and exercise a meaningful application path, not only a port or process start. A green build/test lifecycle is not evidence that the packaged app boots.

A test-infrastructure fix must not accidentally alter production behavior. Necessary compatibility fixes belong with the upgrade or a clearly linked prerequisite; both must be validated together before the upgrade ships. Do not merge a broken intermediate deployment solely to keep PRs separate.

Inspect the resolved runtime dependency tree before and after the upgrade with the same profiles, repositories and build options. Review removals and version substitutions as well as additions; a missing transitive runtime class can pass unit tests and fail during application startup.

For a Maven project, `mvn clean verify` runs the configured build/test lifecycle; it boots the production artifact only if the project explicitly adds that check. Separately launch the packaged jar/container with the project's runtime command, wait for readiness, smoke the affected endpoint or worker, inspect startup errors, and shut it down cleanly. Record the artifact, configuration and observed result. Integration tests in a special test profile do not substitute for this check when their classpath or configuration differs.

Update lockfiles with the package manager and verify clean/frozen installation where the project uses one. Check runtime/toolchain, database driver and test-container compatibility from authoritative release notes when those components move.

## DEP-PIN-SUPPRESS

Every exceptional override, workaround pin or scanner suppression carries:

- Advisory ID for a security workaround; otherwise the compatibility issue or upstream reference.
- Reason and affected version range; for a suppression, why the advisory does not apply or which mitigation covers it.
- Owner and removal/review condition. A temporary suppression has an expiry or explicit review date.

Keep resolved installations reproducible through the project's lockfile/BOM policy. Avoid an open-ended override that could select an untested major version; ordinary declared compatibility ranges need not all become exact pins. Re-check exceptional pins and suppressions when the platform BOM or affected package moves, and verify the override reaches the vulnerable transitive path.

```json
{
  "overrides": {
    "some-package": "1.2.3"
  }
}
```

This is an illustrative root `package.json` npm override, not a verified remediation version. Store rationale/ownership in the project's existing dependency notes or tracker; other package managers have their own override syntax. Update the lockfile and inspect the resolved tree after applying it. Do not extend a suppression expiry without rechecking applicability and available fixes.

## DEP-SLICE

Keep dependency/platform upgrades separate from unrelated feature work so compatibility failures and rollback remain reviewable. Include code changes necessary for the upgrade's compatibility; splitting those into a broken intermediate state defeats the purpose.

Typical triggers:

- BOM upgrade (Quarkus, Spring, etc.)
- Java/Kotlin version upgrade
- CVE remediation
- Test infrastructure changes

Follow the repository's ownership and review rules for affected components. A mixed urgent fix needs an explicit reason and validation of the combined change; a file-count convention must not prevent an atomic security or compatibility repair.

For a CVE, verify the advisory's affected range, runtime reachability/configuration and fixed version from authoritative evidence. Scan the resolved artifact after remediation; merely changing a direct declaration may leave another vulnerable transitive copy. Do not suppress a finding simply to make the scanner green.

## Checklist

- [ ] Upgrade scope excludes unrelated features and includes required compatibility fixes
- [ ] Actual deployable artifact boots, becomes ready and serves the affected path
- [ ] Integration test suite passes
- [ ] Resolved runtime tree diff is reviewed under matching build profiles
- [ ] Exceptional overrides/pins/suppressions have reason, source, owner and removal/review condition
- [ ] Lockfile/BOM resolution is reproducible and exceptional ranges cannot select untested majors
- [ ] Suppressions re-checked when BOM version moves
- [ ] CVE applicability and the resolved remediation are verified
- [ ] Test infrastructure updates validated (Testcontainers, database drivers, etc.)
