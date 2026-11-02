# SQL migrations

Load with the generic rules in the skill. Migrations change shared state that every deployed version reads, so the checks below run against a disposable database before any shared environment is touched.

## Match signals

requires, at least one of:
- A `.sql` migration directory (`db/migration/`, `migrations/`, `src/main/resources/db/migration/`) holding `V<number>__<description>.sql` or `R__<description>.sql` files
- A migration tool signal: Flyway settings in build files or application properties, or a Liquibase changelog (`changelog*.xml`, `changelog*.yaml`)

supporting, never sufficient alone:
- A migrations directory of ORM-generated Python or Ruby files that contain no SQL
- Standalone SQL directories (`sql/`, `scripts/sql/`) used by hand-run jobs

This profile applies only when a required signal is present. An ORM migrations directory with no SQL files does not trigger it.

## Gates

1. Disposable database: apply the migration to a database built from the prior deployed schema, with representative rows including nulls and foreign keys. Paste the tool's output showing the applied versions. A clean empty database alone is not evidence.
2. Idempotency: run seed and repeatable scripts twice. Paste the second run's output, which must apply nothing.
3. Destructive statements: list every drop, truncate, unkeyed delete or update, and type change that rewrites data in the PR body. Each one needs explicit user approval before merge.
4. Environment scope: the PR states which environments the migration runs in, and whether seed rows differ per environment.
5. Backfill: batched and resumable, with bounded locks. The PR states the batch size, the resume key, and the dry-run row count.
6. Rollback or forward fix: named in the PR body, following [delivery](../delivery.md).
7. Scope keys: every new table carries the scope key as a non-nullable column, every new query filters on it, and an index leads with it. Check the plan with `EXPLAIN` at realistic row counts ([performance](../performance.md)).

## Pitfalls

- Applied versioned migrations are immutable: apply [MIGRATE-IMMUTABLE](../workflow.md). Check the migration history table before deciding.
- Seed data belongs in a migration, written idempotently (insert where absent, or upsert on a natural key). Hand-inserted rows differ between environments, and a missing row breaks calls in one environment only.
- Create indexes on existing large tables with the engine's concurrent form, in a non-transactional migration where the tool requires one.
- Expand, then contract, per [MIGRATE-ADDITIVE](../workflow.md). A rename is a drop and an add to running consumers, so it follows the same sequence.
- Set a lock or statement timeout in the migration session, so a blocked `ALTER` fails rather than queueing behind live traffic.
- Keep large data moves out of the schema transaction, and out of the same migration file as the schema change where the tool allows it.
- Repair, clean and validate-skip modes are not used on shared environments without approval. They hide a checksum mismatch instead of resolving it.
- Rollout coexistence and prior-schema testing follow [MIGRATE-ROLLING](../workflow.md). Order the migration before any code that reads the new shape, and state that order in the PR body.

## Pointers

- [tenancy](../tenancy.md): scope keys on tables and queries
- [workflow](../workflow.md): migration rules, gates and PR scope
- [performance](../performance.md): query plans, bounded queries and backfill budgets
- [delivery](../delivery.md): rollout order, readiness and recovery
