# Dependencies, CVEs and upgrades

Version management, CVE remediation, and test infrastructure compatibility.

## DEP-BOOT

After a runtime or BOM upgrade, boot the real app and verify the transitive dependency tree has only expected changes.

A test-infrastructure fix must not alter production behavior. When framework upgrades break the app, isolate the fix in a separate diagnostic PR before shipping the upgrade.

**Example**: Java 21→25 + Quarkus 3.27.5→3.33.3.1 upgrade. Missing Woodstox dependency caused Narayana JTA to crash on every pod. Diagnosed in a follow-up PR and fixed before the upgrade was deemed safe.

```bash
# After upgrade, boot real app
mvn clean verify -pl service
# Diff transitive tree
mvn dependency:tree > after.txt  # Compare to base branch
```

## DEP-PIN-SUPPRESS

Every dependency override, version pin or scanner suppression carries:
- Advisory ID (issue tracker reference)
- Reason (why this pin exists)
- Removal condition (when can it be deleted)

No open-ended `>=` ranges. Re-check when the platform BOM version moves.

```json
{
  "npm": {
    "overrides": {
      "some-package": "1.2.3"
    },
    "_overrideReasons": {
      "some-package": "CVE-2024-1234: XSS in formatter. Remove when >= 2.0 ships. Issue: CG-996"
    }
  }
}
```

**Gap**: Don't extend suppression TTL without re-checking. Stale suppressions hide real problems.

## DEP-SLICE

Dependency or platform upgrades ship in isolation, separate from feature work.

**When**:
- BOM upgrade (Quarkus, Spring, etc.)
- Java/Kotlin version upgrade
- CVE remediation
- Test infrastructure changes

**No feature work in the same PR.** If the upgrade touches code from another team, get explicit approval.

**Example**: CG-996 (Java 21→25, Quarkus 3.33.3.1) was approved before CG-1004 (error enrichment) merged, because one reviewer refused to sign off on a change that touched producer scopes in code they don't own.

## Checklist

- [ ] Dependency upgrade is a separate PR with no feature work
- [ ] Real app boots without errors after upgrade (`mvn clean verify` or equivalent)
- [ ] Integration test suite passes
- [ ] Transitive dependency tree diff is reviewed (no surprise new deps)
- [ ] Every override/pin/suppression has advisory ID, reason, removal condition
- [ ] No `>=` ranges without an upper bound
- [ ] Suppressions re-checked when BOM version moves
- [ ] CVE fixes are urgent and separate from other work
- [ ] Test infrastructure updates validated (Testcontainers, database drivers, etc.)
