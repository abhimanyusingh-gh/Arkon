# JVM Maven service

Profile for a Java or Kotlin service built with Maven. Use with the flat references it points to; the repository's instruction file supplies the exact commands.

## Match signals

- **Requires:** `pom.xml` at the repository root, or a Maven wrapper (`mvnw`).
- Supporting: `src/main/java` or `src/main/kotlin` trees, profile-prefixed `application.properties` keys, `db/migration` directory.

## Gates

Run in this order. Stop at the first red gate.

1. **Format and commit-lint.** [GATE-FORMAT-LINT](../workflow.md). Run them before any other gate; CI fails fast here.
2. **Compile** every module the change touches, not only the changed module.
3. **Unit phase.** [BIND-RUNS-TESTS](../testing.md). Name the surefire phase that runs unit tests and report its nonzero count from the build output.
4. **Integration phase.** Confirm the failsafe or verify binding reaches the integration suite, separate from unit tests. Report its count from the build output.
5. **Vulnerability gate.** [GATE-VULN-ZERO](../workflow.md). Fix the dependency. An accepted-risk suppression follows [DEP-PIN-SUPPRESS](../dependencies.md).

Stack specifics:

- Pin the JDK in the build or the CI definition, for example `maven.compiler.release` or the toolchain plugin. The machine default differs between laptops and CI. [BIND-BLOCKERS](../project-binding.md) gives the general rule.
- Check that the registry token can publish as well as read before a build that pulls private artifacts. A read-only token fails with errors that look like a missing dependency.

## Pitfalls

- **Dead profile-prefixed properties.** A `%profile.` key is dead when the packaged artifact runs under a different profile. Check the deployment configuration for the active profile before trusting a test that depends on one.
- **Migration-tool destructive modes.** Clean, repair and skip-validate never run on a shared environment. [ENV-SHARED-TRIAL](../project-binding.md) and [SEED-MODE](../testing.md) set the bar; [MIGRATE-IMMUTABLE](../workflow.md) covers applied migrations.
- **Environment values in the service.** Hosts, tenant identifiers and endpoint URLs belong in the config repository or the deploy layer, not in the artifact.
- **Seed rows by hand.** A hand-inserted row exists only in the database that received it. A versioned migration reaches every environment.
- **Generic catches.** A catch of `Exception` or `Throwable` hides the failure class the caller needs. See [CATCH-EMPTY](../verification.md).
- **Packaged startup is not the test profile.** Integration tests under a special profile do not prove the packaged jar starts. See [DEP-BOOT](../dependencies.md).

## Pointers

- [testing](../testing.md): seed data, invariant tests, selector rules
- [dependencies](../dependencies.md): upgrades, CVE remediation, suppressions, boot checks
- [workflow](../workflow.md): slicing, migrations, gate order, commit and push rules
- [verification](../verification.md): [REGRESS-DIFF](../verification.md) for refactors, [TEST-NODELETE](../verification.md) for any removed test
- [delivery](../delivery.md): runtime readiness and rollback when the change affects deployment
