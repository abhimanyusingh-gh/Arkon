# Accessibility

A11y findings are correctness findings, not polish. Include them with the working feature: a keyboard-unreachable control is broken behavior. Prefer native elements and established accessible primitives over custom interaction implementations.

## A11Y-DISABLED — choose disabled semantics deliberately

Native `disabled` usually removes a control from sequential keyboard focus and suppresses activation; it does not generally remove the control from the accessibility tree. Use it when native unavailability is the intended interaction, and expose the reason in accessible text.

Use `aria-disabled` when an unavailable action must remain discoverable in the widget's focus model. It does not suppress activation: guard pointer and keyboard handlers and prevent side effects. Test both activation paths. Neither form of disabled state is an authorization boundary.

## A11Y-MODEL — one interaction model per widget

Pick one pattern and implement it whole: roles, keyboard behaviour, and selection semantics from the same pattern. Never mix. A listbox with checkbox children, an `option` role carrying `aria-checked`, or a multi-select reporting `aria-selected` on some children and `aria-checked` on others is unusable in a screen reader — the two models disagree about what "selected" means and assistive technology picks one.

- Multi-select list → either `listbox` + `aria-multiselectable` with `option` children using `aria-selected`, **or** a labelled group of native checkboxes. Not both.
- Name the pattern being implemented in the PR body whenever a composite widget is added, so the reviewer can check it against the whole pattern rather than guessing.
- Keyboard support is part of the pattern, not an extra: arrow-key traversal for composites, Enter/Space activation, Escape dismissal, Home/End where the pattern defines them.

## A11Y-ANNOUNCE — announce after the state settles, never before

A live-region message written before the mutation resolves announces an outcome that has not happened — and announces success for a request that then fails.

- Write to the live region in the settled path, success and failure separately.
- Keep the region mounted with a stable politeness setting; a region that mounts at the same moment its first message arrives is often not announced at all.
- Optimistic UI may announce optimistically only if the rollback also announces.
- Long-running work announces start and completion, not every intermediate tick.

## A11Y-FOCUS — visible focus and reduced motion are required, not optional

Every interactive element has a visible focus indicator with adequate contrast in supported themes; never remove the outline without a replacement. Respect `prefers-reduced-motion` for nonessential motion and provide a reduced/no-motion path as appropriate. Keyboard and screen-reader behavior must remain usable when motion is disabled.

Use the project's styling system to express focus, state, contrast, and motion preferences consistently.

## A11Y-FLOOR — the baseline on every UI PR

- Labels bound to controls. Never placeholder-as-label.
- Icon-only controls carry an accessible name.
- Images carry alt text; empty alt for decorative.
- A meaningful heading hierarchy, following the page's actual structure.
- Dialogs are keyboard-reachable and named. Modal dialogs contain focus, support dismissal where appropriate, and restore focus deliberately; nonmodal dialogs follow their different focus model.
- Meet applicable target-size/spacing requirements; for web controls use at least the WCAG minimum or an allowed equivalent/exception.
- Colour is never the sole carrier of meaning — pair it with text, shape, or an icon.
- Contrast verified in light and dark, not assumed from the token name.
- Dynamic content that replaces a focused element moves focus deliberately; never drop focus to the document body.
