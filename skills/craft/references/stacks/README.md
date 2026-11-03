# Stack profiles

Stack profiles add stack-specific gates and pitfalls on top of the flat references. They are checklists that point back to the rules in `../` and never restate them.

## How to use

1. Read the repository and its instruction file first (for example `CLAUDE.md` or `AGENTS.md`). Its exact commands and conventions come from there, not from a profile.
2. Compare the repository against the match signals below. A profile applies only when its required signal is present; supporting signals alone never select a profile. Several profiles may apply to one repository.
3. Apply each loaded profile's Gates and Pitfalls next to the flat references its Pointers name.
4. Record the profile files read on the contract card, in the `References read` row, for example `craft + stacks/jvm-maven-service.md`.
5. A profile never overrides the repository's own instruction file. If the two disagree, follow the repository file and report the conflict.

## Profiles

| Profile | Match signals |
|---|---|
| [jvm-maven-service](jvm-maven-service.md) | **requires:** `pom.xml` at the root or a Maven wrapper (`mvnw`); supporting: `src/main/java` or `src/main/kotlin`, profile-prefixed `application.properties`, `db/migration` |
| [react-typescript-ui](react-typescript-ui.md) | **requires:** a `react` dependency in `package.json`; supporting: `tsconfig.json`, Jest, Vitest, Cypress or Playwright config, Vite or webpack config, `src/components` or `src/features` |
| [salesforce-apex-lwc](salesforce-apex-lwc.md) | **requires:** `sfdx-project.json` at the root, or a `force-app/` tree containing `*.cls` or `*.trigger` files; supporting: `force-app/` without Apex, `*-meta.xml` beside source, `lwc/` bundles, `objects/`, `permissionsets/` or `profiles/` |
| [config-and-deploy-repos](config-and-deploy-repos.md) | **requires:** a Helm `Chart.yaml`, or `kustomization.yaml`, `HelmRelease` or `GitRepository` manifests in per-environment directories; supporting: `values*.yaml` and `templates/` (Helm), SOPS `sops:` blocks, sealed-secret resources, `.sops.yaml` |
| [sql-migrations](sql-migrations.md) | **requires:** `V<number>__*.sql` or `R__*.sql` files in a migration directory, or a Flyway or Liquibase signal (settings, `changelog*.xml`/`.yaml`); supporting: ORM-generated migration files with no SQL, standalone SQL directories (`sql/`, `scripts/sql/`) |
| [llm-backed-features](llm-backed-features.md) | **requires:** a model-provider SDK import or dependency, or an `llm`/`ai`/model client module wrapping one; supporting: prompt template files, evaluation sets or golden files, cost or budget config keyed by model name |

Required signals are each profile's own requires line. `salesforce-apex-lwc` and `config-and-deploy-repos` had no split, so one was chosen and mirrored in their Match signals sections; their owners should confirm it.

## Discovery output

`scripts/discover_project_context.py` reports what it finds in the repository. Treat that output as evidence to check, not as authority. A match is a reason to read the profile. Confirm it against the files before applying the profile, and do not load a profile only because the script names it.
