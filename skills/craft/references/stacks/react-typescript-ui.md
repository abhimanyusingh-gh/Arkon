# React TypeScript UI

Profile for a React single-page or component application written in TypeScript. Use with the flat references it points to; the repository's instruction file supplies the exact commands.

## Match signals

- **Requires:** a `react` dependency listed in `package.json`.
- Supporting: `tsconfig.json`, a Jest, Vitest, Cypress or Playwright config, a Vite or webpack config, `src/components` or `src/features` directories.

## Gates

Run in this order. Stop at the first red gate.

1. **Typecheck** every workspace the change touches, whole-program, not per file.
2. **Lint** with the repository's configured rules, plus [GATE-FORMAT-LINT](../workflow.md) where the repository runs a formatter. A disable comment needs a stated reason.
3. **Unit tests.** Full unfiltered suite; [BIND-RUNS-TESTS](../testing.md) applies to the Jest or Vitest run. Record pass, fail and skip counts.
4. **Production build.** A development server is not a build; see [DELIVERY-READY](../delivery.md).
5. **End-to-end run** when the change touches markup, routes, composition or shared state. The spec pass ships with the DOM change ([SPEC-PASS](../verification.md)).
6. **Browser not runnable.** Reproduce the claim once ([CLAIM-REPRO](../verification.md)), then report `NOT RUN: <reason>` with the captured error. Never mark it passed.

## Pitfalls

- **Inline styles.** Follow the repository's styling convention. Where it bans inline styles, including style-prop shorthands from the component library, the only runtime exception is assigning a CSS custom property, for example a computed position.
- **CSS-in-JS source order.** A rule injected after the stylesheets wins on source order at equal specificity, so it can silently override a supported override. Diagnose cascade order and layers before adding `!important` or a more specific selector. See [frontend](../frontend.md).
- **Redesigned surfaces need explicit states.** Hand-write the hover, focus and disabled states the library no longer supplies, and check focus against [accessibility](../accessibility.md).
- **Assert the root composition, not a harness.** A test mounted inside a router- or provider-wrapped harness proves the harness. Assert against the real tree. See [HARNESS-MASK](../verification.md).
- **Library-native API first.** [LIB-NATIVE-FIRST](../defect-classes.md) applies, including porting approved mockups verbatim. The reason for any custom CSS goes in the PR body.
- **Test-ID inventory before a refactor.** Search the whole suite, including shared helpers, for every selector that reaches the changed surface. See [ID-INVENTORY](../verification.md).
- **Never delete an assertion to reach green.** [TEST-NODELETE](../verification.md).
- **Accessibility basics on every interactive change.** Labels bound to controls, a keyboard path, a visible focus indicator, and live-region announcements only after the state settles. See [accessibility](../accessibility.md).

## Pointers

- [frontend](../frontend.md): design fidelity, server and local state, bulk mutations
- [accessibility](../accessibility.md): disabled semantics, widget models, announcements, focus
- [testing](../testing.md): E2E rules, selector and test-ID contract
- [verification](../verification.md): [CLAIM-EVIDENCE](../verification.md) and [HARNESS-MASK](../verification.md) for the browser rows
