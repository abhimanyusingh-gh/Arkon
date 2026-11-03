# Salesforce Apex and Lightning Web Components

Load with the generic rules in the skill. This profile adds only the Salesforce-specific checks; it does not repeat the general gates.

## Match signals

- **Requires:** `sfdx-project.json` at the root, or a `force-app/` tree containing `*.cls` or `*.trigger` files.
- Supporting: `force-app/` tree without Apex, `*.cls` or `*.trigger` files outside `force-app/`, `*-meta.xml` files beside source (metadata format), `lwc/<component>/` bundles, `objects/`, `permissionsets/` or `profiles/` directories.

## Gates

1. Bulk safety: no SOQL, DML or callout inside a loop. Add a test that drives more than one batch of records (200 or more) through the trigger and asserts every record's outcome.
2. Governor limits: paste the test-run output showing the SOQL, DML and CPU figures were checked against the limits, or state the path that was not measured.
3. Apex tests: run the repository's test command unfiltered against a scratch org or sandbox and paste the summary line (run, failed, skipped, org coverage). If no org is reachable, write `NOT RUN: no scratch org or sandbox` on that row.
4. Metadata: a check-only deployment of the full change set, including fields, layouts and permission sets the code needs, pasted with its result. A missing field or permission is a deploy failure, not a late surprise.
5. Lightning components: the repository's Jest suite and lint step, unfiltered, pasted. Each component meets [accessibility](../accessibility.md): labels, keyboard path, focus after dialogs close.
6. Deletions: any removed field, object or permission set is a separate reviewed change, because deleting a field deletes its data.

## Pitfalls

- A query inside a per-record helper exhausts the query limit at the 101st record. Collect the Ids first, query once, and index results in a map keyed by Id.
- One trigger per object. Put logic in the handler or action framework the repository already uses, and do not introduce a second framework beside it.
- Coverage is not assertion. A test that runs the code and asserts nothing passes the org threshold and catches nothing. Assert resulting record state, the thrown error, and the negative case (a user without access).
- Build test data through the repository's factory classes, not hand-built records repeated per test. Look up Record Types by `DeveloperName`, never by a hard-coded Id that differs between orgs.
- Wrap asynchronous work (queueable, batch, future) in `Test.startTest` and `Test.stopTest` so it runs inside the test.
- `without sharing` needs a comment that names the reason it is required. Without that reason, the class runs with the sharing of its caller.
- Build SOQL with bind variables. String concatenation of user input is an injection path ([security](../security.md)).
- Use `@AuraEnabled(cacheable=true)` only for read methods. Write methods are never cacheable.
- Child components signal upward with events; a component does not mutate an `@api` property it received.
- Jest tests mock the Apex import module, then assert that the wire emits data, that an error renders, and that a form submits the expected payload.
- Deploy to a scratch org or sandbox through the CLI first. Do not deploy to production unless the user has explicitly authorised that deployment; default to a scratch org or sandbox.

## Pointers

- [testing](../testing.md): test value, invariant tests, negative cases
- [security](../security.md): sharing, injection and input boundaries
- [accessibility](../accessibility.md): components and forms
- [tenancy](../tenancy.md): sharing as the scope boundary, and the negative test
- [workflow](../workflow.md) and [delivery](../delivery.md): gates, slicing and readiness
